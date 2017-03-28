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

import './forms.scss';

export const UserRecoveryCodeForm = ({ t, next }) => (
  <form className='user-code-form' onSubmit={next}>
    <img
      className='account-recovery-progress'
      src='/public/images/account-recovery/step_2.svg'
      alt={t('account-recovery.user-form.image-description')}
    />
    <h1>{t('account-recovery.user-form.title')}</h1>
    <p>{t('account-recovery.user-form.description')}</p>
    <InputField name='admin-code' label={t('account-recovery.user-form.input-label')} />
    <SubmitButton buttonText={t('account-recovery.user-form.button')} />
  </form>
);

UserRecoveryCodeForm.propTypes = {
  t: React.PropTypes.func.isRequired,
  next: React.PropTypes.func.isRequired
};

export default translate('', { wait: true })(UserRecoveryCodeForm);
