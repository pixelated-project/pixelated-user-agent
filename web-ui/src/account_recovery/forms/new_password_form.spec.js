import { shallow } from 'enzyme';
import expect from 'expect';
import React from 'react';
import { NewPasswordForm } from 'src/account_recovery/forms/new_password_form';

describe('NewPasswordForm', () => {
  let newPasswordForm;

  beforeEach(() => {
    const mockTranslations = key => key;
    newPasswordForm = shallow(
      <NewPasswordForm t={mockTranslations} />
    );
  });

  it('renders title for new password form', () => {
    expect(newPasswordForm.find('h1').text()).toEqual('account-recovery.new-password-form.title');
  });

  it('renders input for new password', () => {
    expect(newPasswordForm.find('InputField').at(0).props().label).toEqual('account-recovery.new-password-form.input-label1');
  });

  it('renders input to confirm new password', () => {
    expect(newPasswordForm.find('InputField').at(1).props().label).toEqual('account-recovery.new-password-form.input-label2');
  });

  it('renders submit button', () => {
    expect(newPasswordForm.find('SubmitButton').props().buttonText).toEqual('account-recovery.new-password-form.button');
  });
});
