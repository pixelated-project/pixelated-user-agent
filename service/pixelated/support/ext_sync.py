import leap.soledad.client as client
import logging
import urlparse


def patched_sync(self, autocreate=False, defer_decryption=True):
    sync_target = self.sync_target

    # get target identifier, its current generation,
    # and its last-seen database generation for this source
    ensure_callback = None
    try:
        (self.target_replica_uid, target_gen, target_trans_id,
         target_my_gen, target_my_trans_id) = \
            sync_target.get_sync_info(self.source._replica_uid)
    except errors.DatabaseDoesNotExist:
        if not autocreate:
            raise
        # will try to ask sync_exchange() to create the db
        self.target_replica_uid = None
        target_gen, target_trans_id = (0, '')
        target_my_gen, target_my_trans_id = (0, '')

    logger.debug(
        "Soledad target sync info:\n"
        "  target replica uid: %s\n"
        "  target generation: %d\n"
        "  target trans id: %s\n"
        "  target my gen: %d\n"
        "  target my trans_id: %s\n"
        "  source replica_uid: %s\n"
        % (self.target_replica_uid, target_gen, target_trans_id,
           target_my_gen, target_my_trans_id, self.source._replica_uid))

    # make sure we'll have access to target replica uid once it exists
    if self.target_replica_uid is None:

        def ensure_callback(replica_uid):
            self.target_replica_uid = replica_uid

    # make sure we're not syncing one replica with itself
    if self.target_replica_uid == self.source._replica_uid:
        raise errors.InvalidReplicaUID

    # validate the info the target has about the source replica
    self.source.validate_gen_and_trans_id(
        target_my_gen, target_my_trans_id)

    # what's changed since that generation and this current gen
    my_gen, _, changes = self.source.whats_changed(target_my_gen)
    logger.debug("Soledad sync: there are %d documents to send."
                 % len(changes))

    # get source last-seen database generation for the target
    if self.target_replica_uid is None:
        target_last_known_gen, target_last_known_trans_id = 0, ''
    else:
        target_last_known_gen, target_last_known_trans_id = \
            self.source._get_replica_gen_and_trans_id(
                self.target_replica_uid)
    logger.debug(
        "Soledad source sync info:\n"
        "  source target gen: %d\n"
        "  source target trans_id: %s"
        % (target_last_known_gen, target_last_known_trans_id))

    # validate transaction ids
    if not changes and target_last_known_gen == target_gen:
        if target_trans_id != target_last_known_trans_id:
            raise errors.InvalidTransactionId
        return my_gen

    # prepare to send all the changed docs
    changed_doc_ids = [doc_id for doc_id, _, _ in changes]
    docs_to_send = self.source.get_docs(
        changed_doc_ids, check_for_conflicts=False, include_deleted=True)
    docs_by_generation = []
    idx = 0
    for doc in docs_to_send:
        _, gen, trans = changes[idx]
        docs_by_generation.append((doc, gen, trans))
        idx += 1

    # exchange documents and try to insert the returned ones with
    # the target, return target synced-up-to gen.
    #
    # The sync_exchange method may be interrupted, in which case it will
    # return a tuple of Nones.
    try:
        new_gen, new_trans_id = sync_target.sync_exchange(
            docs_by_generation, self.source._replica_uid,
            target_last_known_gen, target_last_known_trans_id,
            self._insert_doc_from_target, ensure_callback=ensure_callback,
            defer_decryption=defer_decryption)
        logger.debug(
            "Soledad source sync info after sync exchange:\n"
            "  source target gen: %d\n"
            "  source target trans_id: %s"
            % (new_gen, new_trans_id))
        info = {
            "target_replica_uid": self.target_replica_uid,
            "new_gen": new_gen,
            "new_trans_id": new_trans_id,
            "my_gen": my_gen
        }
        self._syncing_info = info
        if defer_decryption and not sync_target.has_syncdb():
            logger.debug("Sync target has no valid sync db, "
                         "aborting defer_decryption")
            defer_decryption = False
        self.complete_sync()
    except Exception as e:
        logger.error("Soledad sync error: %s  - %s" % (e.__class__.__name__, e.message))
        logger.error(traceback.format_exc())
        sync_target.stop()
    finally:
        sync_target.close()

    return my_gen

client.Soledad._sync = patched_sync
