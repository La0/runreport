from django.conf import settings
from payments import get_api
from mangopaysdk.entities.userlegal import UserLegal
from mangopaysdk.entities.wallet import Wallet
from mangopaysdk.types.address import Address
import time
import os
import json


class RRAccount(object):
    '''
    Represents the RunReport account
    on MangoPay so we can receive money !
    '''
    __cache = {}

    def __init__(self):
        self.load()

    @property
    def cache_path(self):
        return os.path.join(settings.MANGOPAY_CACHE, 'rr.json')

    def __getattr__(self, key):
        # Helper to access data from cache
        if self.__cache and key in self.__cache:
            return self.__cache[key]
        return None

    def load(self):
        if not os.path.exists(self.cache_path):
            self.__cache = None

        try:
            self.__cache = json.load(open(self.cache_path, 'r'))
        except BaseException:
            self.__cache = None

    def build(self):
        '''
        Creation workflow
        '''
        u = self.build_user()
        w = self.build_wallet(u)
        self.save(u, w)

    def build_user(self):
        '''
        Build the main RR account
        '''
        if self.Id:
            raise Exception('RR Account already exists')

        # Build address
        address = Address()
        address.AddressLine1 = '40 Rue des Archives'
        address.City = 'Paris'
        address.Country = 'FR'
        address.PostalCode = '75004'

        # Build legal user
        rr_user = UserLegal()
        rr_user.Name = 'RunReport'
        rr_user.LegalPersonType = 'BUSINESS'
        rr_user.LegalRepresentativeFirstName = 'Sylvain'
        rr_user.LegalRepresentativeLastName = 'Darrasse'
        rr_user.LegalRepresentativeAddress = address
        rr_user.LegalRepresentativeEmail = 'sylvain@runreport.fr'
        rr_user.LegalRepresentativeBirthday = int(
            time.mktime((1979, 1, 2, 0, 0, 0, -1, -1, -1)))
        rr_user.LegalRepresentativeNationality = 'FR'
        rr_user.LegalRepresentativeCountryOfResidence = 'FR'
        rr_user.Email = 'contact@runreport.fr'

        # Finally create the user
        api = get_api()
        return api.users.Create(rr_user)

    def build_wallet(self, user):
        '''
        Build a wallet for this account
        '''
        wallet = Wallet()
        wallet.Owners = [user.Id, ]
        wallet.Description = 'Main RunReport wallet'
        wallet.Currency = 'EUR'

        # Create the wallet
        api = get_api()
        return api.wallets.Create(wallet)

    def save(self, user, wallet):
        '''
        Save user & wallet in json cache
        '''
        def __serialize(x):
            # Build objects dict as json
            out = {}
            for k, v in x.__dict__.items():
                if hasattr(v, '__dict__'):
                    out[k] = v.__dict__
                else:
                    out[k] = v
            return out

        # Add user
        save = __serialize(user)

        # Add wallet dict
        save['wallet'] = __serialize(wallet)

        # Save in cache as json
        with open(self.cache_path, 'w') as f:
            f.write(json.dumps(save, indent=4, sort_keys=True))
