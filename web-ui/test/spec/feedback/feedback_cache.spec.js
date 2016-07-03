define(['feedback/feedback_cache'], function (feedbackCache) {
  'use strict';

  describe('feedbackCache', function () {
    it('should cache', function () {
      feedbackCache.resetCache();
      expect(feedbackCache.getCache()).toEqual('');
      feedbackCache.setCache('foo bar');
      expect(feedbackCache.getCache()).toEqual('foo bar');
    });
  });
});
