# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uuid
import bcrypt

from datetime import datetime, timedelta

from mediagoblin.db.sql.base import Base
from mediagoblin.db.models import User

from sqlalchemy import (
        Column, Unicode, Integer, DateTime, ForeignKey, Enum)
from sqlalchemy.orm import relationship

# Don't remove this, I *think* it applies sqlalchemy-migrate functionality onto
# the models.
from migrate import changeset


class OAuthClient(Base):
    __tablename__ = 'oauth__client'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False,
            default=datetime.now)

    name = Column(Unicode)
    description = Column(Unicode)

    identifier = Column(Unicode, unique=True, index=True)
    secret = Column(Unicode, index=True)

    owner_id = Column(Integer, ForeignKey(User.id))
    owner = relationship(User, backref='registered_clients')

    redirect_uri = Column(Unicode)

    type = Column(Enum(
        u'confidential',
        u'public',
        name=u'oauth__client_type'))

    def generate_identifier(self):
        self.identifier = unicode(uuid.uuid4())

    def generate_secret(self):
        self.secret = unicode(
                bcrypt.hashpw(
                    unicode(uuid.uuid4()),
                    bcrypt.gensalt()))

    def __repr__(self):
        return '<{0} {1}:{2} ({3})>'.format(
                self.__class__.__name__,
                self.id,
                self.name.encode('ascii', 'replace'),
                self.owner.username.encode('ascii', 'replace'))


class OAuthUserClient(Base):
    __tablename__ = 'oauth__user_client'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, backref='oauth_clients')

    client_id = Column(Integer, ForeignKey(OAuthClient.id))
    client = relationship(OAuthClient, backref='users')

    state = Column(Enum(
        u'approved',
        u'rejected',
        name=u'oauth__relation_state'))

    def __repr__(self):
        return '<{0} #{1} {2} [{3}, {4}]>'.format(
                self.__class__.__name__,
                self.id,
                self.state.encode('ascii', 'replace'),
                self.user,
                self.client)


class OAuthToken(Base):
    __tablename__ = 'oauth__tokens'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False,
            default=datetime.now)
    expires = Column(DateTime, nullable=False,
            default=lambda: datetime.now() + timedelta(days=30))
    token = Column(Unicode, index=True)
    refresh_token = Column(Unicode, index=True)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False,
            index=True)
    user = relationship(User)

    client_id = Column(Integer, ForeignKey(OAuthClient.id), nullable=False)
    client = relationship(OAuthClient)

    def __repr__(self):
        return '<{0} #{1} expires {2} [{3}, {4}]>'.format(
                self.__class__.__name__,
                self.id,
                self.expires.isoformat(),
                self.user,
                self.client)


class OAuthCode(Base):
    __tablename__ = 'oauth__codes'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False,
            default=datetime.now)
    expires = Column(DateTime, nullable=False,
            default=lambda: datetime.now() + timedelta(minutes=5))
    code = Column(Unicode, index=True)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False,
            index=True)
    user = relationship(User)

    client_id = Column(Integer, ForeignKey(OAuthClient.id), nullable=False)
    client = relationship(OAuthClient)

    def __repr__(self):
        return '<{0} #{1} expires {2} [{3}, {4}]>'.format(
                self.__class__.__name__,
                self.id,
                self.expires.isoformat(),
                self.user,
                self.client)


MODELS = [
        OAuthToken,
        OAuthCode,
        OAuthClient,
        OAuthUserClient]
