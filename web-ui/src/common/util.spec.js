import expect from 'expect';
import fetchMock from 'fetch-mock';

import browser from 'helpers/browser';
import Util from 'src/common/util';

describe('Utils', () => {
  describe('.hasQueryParameter', () => {
    before(() => {
      global.window = { location: { search: '?auth-error&lng=pt-BR' } };
    });

    it('checks if param included in query parameters', () => {
      expect(Util.hasQueryParameter('auth-error')).toBe(true);
    });

    it('checks if param not included in query parameters', () => {
      expect(Util.hasQueryParameter('error')).toBe(false);
    });
  });

  describe('.getQueryParameter', () => {
    before(() => {
      global.window = { location: { search: '?auth-error&lng=pt-BR' } };
    });

    it('gets value of param included in query parameters', () => {
      expect(Util.getQueryParameter('lng')).toBe('pt-BR');
    });

    it('returns empty if param does not have value', () => {
      expect(Util.getQueryParameter('auth-error')).toBe(null);
    });

    it('returns undefined if param is not included in query parameters', () => {
      expect(Util.getQueryParameter('username')).toBe(undefined);
    });
  });

  describe('submitForm', () => {
    const event = {};

    beforeEach(() => {
      event.preventDefault = expect.createSpy();
      expect.spyOn(browser, 'getCookie').andReturn('abc123');

      fetchMock.post('/some-url', 200);
      Util.submitForm(event, '/some-url', { userCode: '123' });
    });

    it('sends csrftoken as content', () => {
      expect(fetchMock.lastOptions('/some-url').body).toContain('"csrftoken":["abc123"]');
    });

    it('sends body as content', () => {
      expect(fetchMock.lastOptions('/some-url').body).toContain('"userCode":"123"');
    });

    it('sends content-type header', () => {
      expect(fetchMock.lastOptions('/some-url').headers['Content-Type']).toEqual('application/json');
    });

    it('sends same origin headers', () => {
      expect(fetchMock.lastOptions('/some-url').credentials).toEqual('same-origin');
    });

    it('prevents default call to refresh page', () => {
      expect(event.preventDefault).toHaveBeenCalled();
    });
  });
});
