/* global Pixelated */

describeComponent('mail_view/ui/draft_button', function(){
  'use strict';

  describe('draft save button', function(){
    beforeEach(function(){
      this.setupComponent('<button></button>');
    });

    describe('after initialize', function(){
      it('should be enabled', function(){
        expect(this.$node).toBeDisabled();
      });
    });

    describe('when enabled', function(){
      beforeEach(function(){
        this.$node.prop('disabled', false);
      });

      it('should be disabled when saving draft message', function(){
        $(document).trigger(Pixelated.events.mail.saveDraft, {});
        expect(this.$node).toBeDisabled();
      });
    });

    describe('when disabled', function(){
      beforeEach(function(){
        this.$node.prop('disabled', true);
      });

      it('should be enabled when draft message has been saved', function(){
        $(document).trigger(Pixelated.events.mail.draftSaved, {});
        expect(this.$node).not.toBeDisabled();
      });
    });

  });
});
