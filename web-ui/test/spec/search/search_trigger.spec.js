describeComponent('search/search_trigger', function () {
  'use strict';
  var self;

  beforeEach(function () {
    this.setupComponent();
    self = this;
  });

  function submitSearch(queryString) {
    self.component.select('input').val(queryString);
    self.component.select('form').submit();
  }

  it('should trigger search when the submit occurs', function () {
    var spy = spyOnEvent(document, Pixelated.events.search.perform);

    submitSearch('tanana');
    expect(spy).toHaveBeenTriggeredOnAndWith(document, { query: 'tanana' });
  });

  it('should clear input when selecting a new tag', function(){
    submitSearch('tanana');
    $(document).trigger(Pixelated.events.ui.tag.selected, { tag: 'inbox'});
    expect(self.component.select('input').val()).toBe('');
  });

  it('should add place holder on input value after doing a search', function(){
    submitSearch('teste');
    expect(self.component.select('input').val()).toBe('Search results for: teste');
  });

  it('should remove place holder on input value when input is on focus', function(){
    submitSearch('teste');
    this.component.select('input').focus();
    expect(self.component.select('input').val()).toBe('teste');
  });

  it('should remove place holder on input value when input is not on focus', function(){
    submitSearch('teste');
    this.component.select('input').focus();
    this.component.select('input').blur();
    expect(self.component.select('input').val()).toBe('Search results for: teste');
  });

  it('should not change input value when input is empty', function(){
    submitSearch('');
    this.component.select('input').focus();
    expect(self.component.select('input').val()).toBe('');
  });

  it('should focus search input field on focus event', function () {
    $(document).trigger(Pixelated.events.search.focus);

    expect($(document.activeElement)).toEqual(this.component.select('input'));
  });
});
