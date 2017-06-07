/*
 * Copyright (c) 2017 ThoughtWorks, Inc.
 *
 * Pixelated is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Pixelated is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
 */

import 'isomorphic-fetch';
import React from 'react';
import { translate } from 'react-i18next';
import validator from 'validator';

import { submitForm } from 'src/common/util';
import InputField from 'src/common/input_field/input_field';
import SubmitButton from 'src/common/submit_button/submit_button';
import BackLink from 'src/common/back_link/back_link';

import './new_password_form.scss';

export class NewPasswordForm extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      submitButtonDisabled: true,
      password: '',
      errorPassword: '',
      confirmPassword: '',
      errorConfirmPassword: ''
    };
  }

  submitHandler = (event) => {
    event.preventDefault();
    submitForm(event, '/account-recovery', {
      username: this.props.username,
      userCode: this.props.userCode,
      password: this.state.password,
      confirmPassword: this.state.confirmPassword
    }).then((response) => {
      if (response.ok) this.props.next();
      else if (response.status === 401) this.props.onError('error.recovery-auth');
      else this.props.onError('error.general');
    });
  };

  handleChangePassword = (event) => {
    this.setState({ password: event.target.value });
    this.validatePassword(event.target.value, this.state.confirmPassword);
  };

  handleChangeConfirmPassword = (event) => {
    this.setState({ confirmPassword: event.target.value });
    this.validatePassword(this.state.password, event.target.value);
  };

  validatePassword = (password, confirmPassword) => {
    const emptyPassword = validator.isEmpty(password);
    const validPassword = validator.isLength(password, { min: 8, max: 9999 });
    const emptyConfirmPassword = validator.isEmpty(confirmPassword);
    const validConfirmPassword = confirmPassword === password;

    const t = this.props.t;

    this.setState({
      errorPassword: !emptyPassword && !validPassword ? t('account-recovery.new-password-form.error.invalid-password') : '',
      errorConfirmPassword: !emptyConfirmPassword && !validConfirmPassword ? t('account-recovery.new-password-form.error.invalid-confirm-password') : '',
      submitButtonDisabled: !validPassword || !validConfirmPassword
    });
  };

  render() {
    const { t, previous } = this.props;
    return (
      <form className='account-recovery-form new-password' onSubmit={this.submitHandler}>
        <img
          className='account-recovery-progress'
          src='/public/images/account-recovery/step_3.svg'
          alt={t('account-recovery.new-password-form.image-description')}
        />
        <h1>{t('account-recovery.new-password-form.title')}</h1>
        <InputField
          type='password' name='new-password' value={this.state.password}
          label={t('account-recovery.new-password-form.input-label1')}
          errorText={this.state.errorPassword} onChange={this.handleChangePassword}
        />
        <InputField
          type='password' name='confirm-password' value={this.state.confirmPassword}
          label={t('account-recovery.new-password-form.input-label2')}
          errorText={this.state.errorConfirmPassword} onChange={this.handleChangeConfirmPassword}
        />
        <SubmitButton buttonText={t('account-recovery.button-next')} disabled={this.state.submitButtonDisabled} />
        <BackLink text={t('account-recovery.back')} onClick={previous} />
      </form>
    );
  }
}

NewPasswordForm.propTypes = {
  t: React.PropTypes.func.isRequired,
  next: React.PropTypes.func.isRequired,
  previous: React.PropTypes.func.isRequired,
  username: React.PropTypes.string.isRequired,
  userCode: React.PropTypes.string.isRequired,
  onError: React.PropTypes.func.isRequired
};

export default translate('', { wait: true })(NewPasswordForm);
