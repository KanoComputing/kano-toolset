#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg


stage ('Build') {
    build_deb_pkg 'kano-toolset', env.BRANCH_NAME, 'scratch'
}
