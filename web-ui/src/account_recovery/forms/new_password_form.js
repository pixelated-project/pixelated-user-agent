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

import React from 'react';
import { translate } from 'react-i18next';

import InputField from 'src/common/input_field/input_field';
import SubmitButton from 'src/common/submit_button/submit_button';

export const NewPasswordForm = ({ t }) => (
  <form>
    <img
      className='account-recovery-progress'
      src='/public/images/account-recovery/step_3.svg'
      alt={t('account-recovery.new-password.image-description')}
    />
    <h1>{t('account-recovery.new-password-form.title')}</h1>
    <InputField name='new-password' label={t('account-recovery.new-password-form.input-label1')} />
    <InputField name='confirm-password' label={t('account-recovery.new-password-form.input-label2')} />
    <SubmitButton buttonText={t('account-recovery.new-password-form.button')} />
  </form>
);

NewPasswordForm.propTypes = {
  t: React.PropTypes.func.isRequired
};

export default translate('', { wait: true })(NewPasswordForm);
