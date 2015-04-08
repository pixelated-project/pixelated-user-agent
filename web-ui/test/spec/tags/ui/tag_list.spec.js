describeComponent('tags/ui/tag_list', function () {
  'use strict';
  var tagsShortcutsContainer;

  var tag = function (name, ident, def) {
    def = def || false;
    return {name: name, counts: {read: 0, total: 0, replied: 0, starred: 0}, ident: ident, default: def};
  };


  describe('post initialization', function () {
    beforeEach(function () {
      this.setupComponent();
      tagsShortcutsContainer = $('<ul>', { id: 'tags-shortcuts' });
      $('body').append(tagsShortcutsContainer);
    });

    afterEach(function () {
      $('body')[0].removeChild(tagsShortcutsContainer[0]);
    });

    it('should render tags when tagsList:load is received', function () {
      this.component.attr.default = false;
      var tagList = [tag('tag1', 1), tag('tag2', 2), tag('tag3', 3)];

      $(document).trigger(Pixelated.events.tags.received, {tags: tagList});

      var items = _.map(this.$node.find('li'), function (el) {
        return $(el).attr('id');
      });

      expect(items).toEqual(['tag-1', 'tag-2', 'tag-3']);
    });

    it('should render the default tags when tagsList:load is received and default attribute is true', function () {
      var tagList = [tag('tag1', 1, false), tag('tag2', 2, true), tag('tag3', 3, true)];

      $(document).trigger(Pixelated.events.tags.received, {tags: tagList});

      var items = _.map(this.component.select('defaultTagList').find('li'), function (el) {
        return $(el).attr('id');
      });

      expect(items).toEqual(['tag-2', 'tag-3']);
    });

    it('should render the custom tags when tagsList:load is received and default attribute is false', function () {
      var tagList = [tag('tag1', 1, false), tag('tag2', 2, true), tag('tag3', 3, true)];

      $(document).trigger(Pixelated.events.tags.received, {tags: tagList});

      var items = _.map(this.component.select('customTagList').find('li'), function (el) {
        return $(el).attr('id');
      });

      expect(items).toEqual(['tag-1']);
    });

    it('should save the current tag when a tag is selected', function () {
      $(document).trigger(Pixelated.events.ui.tag.select, { tag: 'amazing'});

      expect(this.component.attr.currentTag).toEqual('amazing');
    });

    it('should uncheck all emails when a new tag is selected', function () {
      var uncheckAllEvent = spyOnEvent(document, Pixelated.events.ui.mails.uncheckAll);
      $(document).trigger(Pixelated.events.ui.tag.select, { tag: 'amazing'});

      expect(uncheckAllEvent).toHaveBeenTriggeredOn(document);
    });

    it('resets the tag lists when loading tags', function () {
      var tagList = [tag('tag1', 1, false), tag('tag2', 2, true), tag('tag3', 3, true)];
      $(document).trigger(Pixelated.events.tags.received, {tags: tagList});

      tagList = [tag('tag1', 1, false), tag('tag2', 2, true)];
      $(document).trigger(Pixelated.events.tags.received, {tags: tagList});

      var customTags = _.map(this.component.select('customTagList').find('li'), function (el) {
        return $(el).attr('id');
      });
      var defaultTags = _.map(this.component.select('defaultTagList').find('li'), function (el) {
        return $(el).attr('id');
      });

      expect(customTags).toEqual(['tag-1']);
      expect(defaultTags).toEqual(['tag-2']);
    });

    it('sends teardown events when loading new tags', function () {
      var tagsTeardownCustom = spyOnEvent(this.component.select('customTagList'), Pixelated.events.tags.teardown);
      var tagsTeardownDefault = spyOnEvent(this.component.select('defaultTagList'), Pixelated.events.tags.teardown);

      $(document).trigger(Pixelated.events.tags.received, {tags: []});

      expect(tagsTeardownCustom).toHaveBeenTriggeredOn(this.component.select('customTagList'));
      expect(tagsTeardownDefault).toHaveBeenTriggeredOn(this.component.select('defaultTagList'));
    });
  });
});
