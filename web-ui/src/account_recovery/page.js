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
import DocumentTitle from 'react-document-title';
import Header from 'src/common/header/header';
import AdminRecoveryCodeForm from 'src/account_recovery/admin_recovery_code_form/admin_recovery_code_form';
import UserRecoveryCodeForm from 'src/account_recovery/user_recovery_code_form/user_recovery_code_form';
import NewPasswordForm from 'src/account_recovery/new_password_form/new_password_form';
import BackupAccountStep from 'src/account_recovery/backup_account_step/backup_account_step';
import Footer from 'src/common/footer/footer';
import Util from 'src/common/util';
import SnackbarNotification from 'src/common/snackbar_notification/snackbar_notification';

import 'font-awesome/scss/font-awesome.scss';
import './page.scss';


export class Page extends React.Component {

  constructor(props) {
    super(props);
    this.state = { step: 0, userCode: '', username: this.setUsername(), errorMessage: '' };
  }

  setUsername = () => (Util.getQueryParameter('username') || '');

  nextStep = (event) => {
    if (event) {
      event.preventDefault();
    }
    this.setState({ step: this.state.step + 1 });
  };

  previousStep = () => {
    this.setState({ step: this.state.step - 1 });
  };

  saveUserCode = (event) => {
    this.setState({ userCode: event.target.value });
  };

  errorHandler = (errorMessage) => {
    this.setState({ errorMessage });
  };

  steps = () => ({
    0: <AdminRecoveryCodeForm next={this.nextStep} />,
    1:
      (<UserRecoveryCodeForm
        previous={this.previousStep}
        next={this.nextStep}
        saveCode={this.saveUserCode}
      />),
    2:
      (<NewPasswordForm
        previous={this.previousStep}
        userCode={this.state.userCode}
        next={this.nextStep}
        username={this.state.username}
        onError={this.errorHandler}
      />),
    3: <BackupAccountStep />
  });

  mainContent = () => this.steps()[this.state.step];

  showSnackbarOnError = (t) => {
    if (this.state.errorMessage) {
      return <SnackbarNotification message={t(this.state.errorMessage)} isError />;
    }
    return undefined; // To satisfy eslint error - consistent-return
  };

  render() {
    const t = this.props.t;
    return (
      <DocumentTitle title={t('account-recovery.page-title')}>
        <div className='page'>
          <Header />
          <section>
            <div className='container'>
              {this.mainContent()}
            </div>
          </section>
          {this.showSnackbarOnError(t)}
          <Footer />
        </div>
      </DocumentTitle>
    );
  }
}

Page.propTypes = {
  t: React.PropTypes.func.isRequired
};

export default translate('', { wait: true })(Page);
