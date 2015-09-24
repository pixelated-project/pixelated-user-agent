'use strict';

describeComponent('page/pane_contract_expand', function () {

  var fixture;

  beforeEach(function () {
    fixture = $('<div>')
      .append($('<div>', { id: 'middle-pane-container' }))
      .append($('<div>', { id: 'right-pane' }));

    $('body').append(fixture);


  });

  afterEach(function () {
    fixture.remove();
  });

  describe('after initialization', function () {
    beforeEach(function () {
      this.setupComponent(document);
    });

    it('contracts middle pane and expands right pane on mail open', function () {
      $(document).trigger(Pixelated.events.ui.mail.open);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_CONTRACT_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_EXPAND_CLASSES);
    });

    it('contracts middle pane and expands right pane on open compose box', function () {
      $(document).trigger(Pixelated.events.dispatchers.rightPane.openComposeBox);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_CONTRACT_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_EXPAND_CLASSES);
    });

    it('contracts middle pane and expands right pane on open draft', function () {
      $(document).trigger(Pixelated.events.dispatchers.rightPane.openDraft);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_CONTRACT_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_EXPAND_CLASSES);
    });

    it('contracts middle pane and expands right pane on open draft', function () {
      $(document).trigger(Pixelated.events.dispatchers.rightPane.openFeedbackBox);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_CONTRACT_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_EXPAND_CLASSES);
    });

    it('expands middle pane and contracts right pane on event on open no message selected pane', function () {
      $(document).trigger(Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_EXPAND_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_CONTRACT_CLASSES);
    });
  });

  describe('on initialization', function () {
    it('expands middle pane and contracts right pane', function () {
      this.setupComponent(document);

      expect($('#middle-pane-container').attr('class')).toEqual(this.component.attr.MIDDLE_PANE_EXPAND_CLASSES);
      expect($('#right-pane').attr('class')).toEqual(this.component.attr.RIGHT_PANE_CONTRACT_CLASSES);
    });
  });

});
