#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg
import python_test_env


stage ('Test') {
    python_test_env(['kano-i18n']) { python_path_var ->
    }
}


stage ('Build') {
    autobuild_repo_pkg 'kano-toolset'
}
