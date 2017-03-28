import { shallow } from 'enzyme';
import expect from 'expect';
import React from 'react';

import { Page } from 'src/account_recovery/page';
import Header from 'src/common/header/header';
import AdminRecoveryCodeForm from 'src/account_recovery/forms/admin_recovery_code_form';
import UserRecoveryCodeForm from 'src/account_recovery/forms/user_recovery_code_form';
import NewPasswordForm from 'src/account_recovery/forms/new_password_form';
import Footer from 'src/common/footer/footer';

describe('Account Recovery Page', () => {
  let page;

  beforeEach(() => {
    const mockTranslations = key => key;
    page = shallow(<Page t={mockTranslations} />);
  });

  it('renders account recovery page title', () => {
    expect(page.props().title).toEqual('account-recovery.page-title');
  });

  it('renders header', () => {
    expect(page.find(Header).length).toEqual(1);
  });

  it('renders footer', () => {
    expect(page.find(Footer).length).toEqual(1);
  });

  context('main content', () => {
    let pageInstance;

    beforeEach(() => {
      pageInstance = page.instance();
    });

    it('renders admin recovery code form as default form', () => {
      expect(page.find(AdminRecoveryCodeForm).length).toEqual(1);
      expect(page.find(UserRecoveryCodeForm).length).toEqual(0);
      expect(page.find(NewPasswordForm).length).toEqual(0);
    });

    it('renders user recovery code form when admin code submitted', () => {
      pageInstance.nextStep({ preventDefault: () => {} });

      expect(page.find(AdminRecoveryCodeForm).length).toEqual(0);
      expect(page.find(UserRecoveryCodeForm).length).toEqual(1);
      expect(page.find(NewPasswordForm).length).toEqual(0);
    });

    it('renders new password form when user code submitted', () => {
      pageInstance.nextStep({ preventDefault: () => {} });
      pageInstance.nextStep({ preventDefault: () => {} });

      expect(page.find(AdminRecoveryCodeForm).length).toEqual(0);
      expect(page.find(UserRecoveryCodeForm).length).toEqual(0);
      expect(page.find(NewPasswordForm).length).toEqual(1);
    });
  });
});
