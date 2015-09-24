describeComponent('dispatchers/right_pane_dispatcher', function () {
  'use strict';

  describe('after initialization', function () {
    beforeEach(function () {
      this.setupComponent();
    });

    it('listens to open compose box event and creates a compose box', function () {
      var composeBox = require('mail_view/ui/compose_box');
      spyOn(composeBox, 'attachTo');

      this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openComposeBox);

      expect(composeBox.attachTo).toHaveBeenCalled();
    });

    describe('no message selected', function () {
      var noMessageSelectedPane;
      beforeEach(function () {
        noMessageSelectedPane = require('mail_view/ui/no_message_selected_pane');
        spyOn(noMessageSelectedPane, 'attachTo');
      });

      it('listen to open no message selected event and creates a no-message-selected-pane', function () {
        this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

        expect(noMessageSelectedPane.attachTo).toHaveBeenCalled();
      });

      it('sends an dispatchers.middlePane.unselect event', function () {
        var unselectEvent = spyOnEvent(document, Pixelated.events.dispatchers.middlePane.cleanSelected);
        this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

        expect(unselectEvent).toHaveBeenTriggeredOn(document);
      });

      it('pushes the current state with the current tag', function () {
        var pushStateEvent = spyOnEvent(document, Pixelated.events.router.pushState);

        this.component.attr.currentTag = 'sometag';
        this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

        expect(pushStateEvent).toHaveBeenTriggeredOnAndWith(document, jasmine.objectContaining({tag: this.component.attr.currentTag }));
      });

      it('pushes the current state stating that it meant to close the right pane', function () {
        var pushStateEvent = spyOnEvent(document, Pixelated.events.router.pushState);

        this.component.attr.currentTag = 'sometag';
        this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

        expect(pushStateEvent).toHaveBeenTriggeredOnAndWith(document, jasmine.objectContaining({ isDisplayNoMessageSelected:  true }));
      });

      it('listens to open feedback event and open feedback box', function () {
        var feedbackBox = require('mail_view/ui/feedback_box');
        spyOn(feedbackBox, 'attachTo');

        this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openFeedbackBox);

        expect(feedbackBox.attachTo).toHaveBeenCalled();
      });

    });

    it('listens to open a draft and creates it', function () {
      var draftBox = require('mail_view/ui/draft_box');
      spyOn(draftBox, 'attachTo');

      this.component.trigger(document, Pixelated.events.dispatchers.rightPane.openDraft, { ident: '1' });

      expect(draftBox.attachTo).toHaveBeenCalled();
    });
  });


  describe('on initialization', function () {
    var noMessageSelectedPane;

    beforeEach(function () {
      noMessageSelectedPane = require('mail_view/ui/no_message_selected_pane');
      spyOn(noMessageSelectedPane, 'attachTo');
    });

    it('opens the no message selected pane but doesnt push the state', function () {
      var pushStateEvent = spyOnEvent(document, Pixelated.events.router.pushState);

      this.setupComponent();

      expect(noMessageSelectedPane.attachTo).toHaveBeenCalled();
      expect(pushStateEvent).not.toHaveBeenTriggeredOn(document);

    });
  });

});
