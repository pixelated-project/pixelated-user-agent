from leap.mail.incoming.service import IncomingMail


def mark_as_encrypted_inline(f):

    def w(*args, **kwargs):
        msg, valid_sign = f(*args)
        is_encrypted = fetch.PGP_BEGIN in args[1].as_string() and fetch.PGP_END in args[1].as_string()
        decrypted_successfully = fetch.PGP_BEGIN not in msg.as_string() and fetch.PGP_END not in msg.as_string()

        if not is_encrypted:
            encrypted = 'false'
        else:
            if decrypted_successfully:
                encrypted = 'true'
            else:
                encrypted = 'fail'

        msg.add_header('X-Pixelated-encryption-status', encrypted)
        return msg, valid_sign

    return w


def mark_as_encrypted_multipart(f):

    def w(*args, **kwargs):
        msg, valid_sign = f(*args)
        msg.add_header('X-Pixelated-encryption-status', 'true')
        return msg, valid_sign
    return w


IncomingMail._maybe_decrypt_inline_encrypted_msg = mark_as_encrypted_inline(IncomingMail._maybe_decrypt_inline_encrypted_msg)
IncomingMail._decrypt_multipart_encrypted_msg = mark_as_encrypted_multipart(IncomingMail._decrypt_multipart_encrypted_msg)
