import { mount } from 'enzyme';
import expect from 'expect';
import React from 'react';
import App from 'src/common/app';
import AccountRecoveryPage from 'src/account_recovery/page';
import BackupAccountPage from 'src/backup_account/page';
import LoginPage from 'src/login/page';
import testI18n from './i18n';

describe('Translations', () => {
  context('Account Recovery Page', () => {
    it('translates all keys on first step', () => {
      const app = mount(<App i18n={testI18n} child={<AccountRecoveryPage />} />);
      expect(app.text()).toNotContain('untranslated', 'Unstranslated message found in the text: ' + app.text());
    });

    it('translates all keys on second step', () => {
      const app = mount(<App i18n={testI18n} child={<AccountRecoveryPage />} />);
      app.find('form.admin-code-form').simulate('submit');

      expect(app.text()).toNotContain('untranslated', 'Unstranslated message found in the text: ' + app.text());
    });

    it('translates all keys on third step', () => {
      const app = mount(<App i18n={testI18n} child={<AccountRecoveryPage />} />);
      app.find('form.admin-code-form').simulate('submit');
      app.find('form.user-code-form').simulate('submit');

      expect(app.text()).toNotContain('untranslated', 'Unstranslated message found in the text: ' + app.text());
    });
  });

  context('Backup Account Page', () => {
    it('translates all key', () => {
      const app = mount(<App i18n={testI18n} child={<BackupAccountPage />} />);
      expect(app.text()).toNotContain('untranslated', 'Unstranslated message found in the text: ' + app.text());
    });
  });

  context('Login Page', () => {
    it('translates all key', () => {
      const app = mount(<App i18n={testI18n} child={<LoginPage />} />);
      expect(app.text()).toNotContain('untranslated', 'Unstranslated message found in the text: ' + app.text());
    });
  });
});
