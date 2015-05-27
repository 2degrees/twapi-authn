##############################################################################
#
# Copyright (c) 2015, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of twapi-authn
# <https://github.com/2degrees/twapi-authn>, which is subject to the
# provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from nose.tools import assert_false
from nose.tools import assert_raises
from nose.tools import eq_
from nose.tools import ok_
from twapi.connection.exc import NotFoundError
from twapi.connection.testing import MockConnection
from twapi.connection.testing import SuccessfulAPICall
from twapi.connection.testing import UnsuccessfulAPICall

from tests.utils import get_uuid4_str
from twapi.authn import AccessTokenError
from twapi.authn import claim_access_token
from twapi.authn import is_session_active


class TestAuthnTokenClaiming(object):

    def test_valid_token(self):
        expected_user_id = 1
        access_token = get_uuid4_str()

        path_info = '/sessions/{}/'.format(access_token)
        api_call = SuccessfulAPICall(
            path_info,
            'POST',
            response_body_deserialization=expected_user_id,
            )
        with _make_connection(api_call) as connection:
            user_id = claim_access_token(connection, access_token)

        eq_(expected_user_id, user_id)

    def test_invalid_token(self):
        access_token = get_uuid4_str()

        path_info = '/sessions/{}/'.format(access_token)
        api_call = UnsuccessfulAPICall(
            path_info,
            'POST',
            exception=NotFoundError(),
            )
        with assert_raises(AccessTokenError):
            with _make_connection(api_call) as connection:
                claim_access_token(connection, access_token)


class TestSessionIsActive(object):

    def test_active_session(self):
        access_token = get_uuid4_str()
        path_info = '/sessions/{}/'.format(access_token)
        api_call = SuccessfulAPICall(
            path_info,
            'HEAD',
            response_body_deserialization=None,
            )
        with _make_connection(api_call) as connection:
            is_active = is_session_active(connection, access_token)

        ok_(is_active)

    def test_inactive_session(self):
        access_token = get_uuid4_str()
        path_info = '/sessions/{}/'.format(access_token)
        api_call = UnsuccessfulAPICall(
            path_info,
            'HEAD',
            exception=NotFoundError(),
            )
        with _make_connection(api_call) as connection:
            is_active = is_session_active(connection, access_token)

        assert_false(is_active)


def _make_connection(api_call):
    connection = MockConnection(lambda: [api_call])
    return connection
