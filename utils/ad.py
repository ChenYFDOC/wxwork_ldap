import ldap
import sys
import json
from utils.log import logger
from config import settings


class LDAP_Client:
    def __init__(self):
        self.cli = ldap.initialize(settings['ldap_host'], bytes_mode=False)

        # 以下需要开启TLS
        # self.cli = ldap.initialize('ldaps://172.17.0.3:389', bytes_mode=False)
        self.cli.protocol_version = 3
        # cli.set_option(ldap.OPT_REFERRALS, 0)
        # cli.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # cli.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        # ret = self.cli.simple_bind('administrator@huangchao.com', 'Abcd1234')
        ret = self.cli.simple_bind_s(settings['ldap_admin'], settings['ldap_admin_pw'])
        if ret[0] != 97:
            print('帐号认真失败')
            sys.exit(1)

    def __del__(self):
        try:
            self.cli.unbind()
        except:
            pass

    def add_group(self, base_dn):
        """
        base_dn: 需要添加的节点
        """
        dn_list = base_dn.split(',')
        cn = ''
        for item in dn_list:
            attr, value = item.split('=')
            if attr == 'cn':
                cn = value
                break
        add_record = [('objectclass', [b'top', b'posixGroup']),
                      ('cn', [cn.encode()]),
                      ('gidNumber', [self.get_last_gid().encode()]),
                      ]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加组失败:' + str(e))
            return False
        else:
            if result[0] == 105:
                return True
            else:
                logger.error('添加组失败: ' + json.dumps(result))
                return False

    def add_department(self, base_dn):
        """
        base_dn:
        """
        dn_list = base_dn.split(',')
        ou = ''
        for item in dn_list:
            attr, value = item.split('=')
            if attr == 'ou':
                ou = value
                break
        add_record = [('objectclass', [b'top', b'organizationalUnit']),
                      ('ou', [ou.encode()]), ]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加部门失败: ' + str(e))
            return False
        else:
            if result[0] == 105:
                logger.info('添加部门' + base_dn)
                return True
            else:
                logger.error('添加部门失败: ' + json.dumps(result))
                return False

    def add_user(self, base_dn, password=None, email=None):
        """
        base_dn:
        """
        dn_list = base_dn.split(',')
        cn = dn_list[0].split('=')[1]
        group_name = dn_list[1].split('=')[1]
        gid = self.cli.search_s('dc=weiwen,dc=com', ldap.SCOPE_SUBTREE, 'cn={}'.format(group_name))[0][1]['gidNumber'][
            0]
        add_record = [('objectclass', [b'top', b'posixAccount', b'inetOrgPerson', b'organizationalPerson']),
                      ('cn', [cn.encode(), ]),
                      ('sn', [cn.encode(), ]),
                      ('userpassword', [password.encode()],),
                      ('gidNumber', [gid]),
                      ('homeDirectory', ['/home/users/{}'.format(cn).encode()]),
                      ('uidNumber', [self.get_last_uid().encode()]),
                      ('uid', [self.get_last_uid().encode()]),
                      ('mail', [email.encode()]),
                      ]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加用户失败: ' + str(e))
            return False
        else:
            if result[0] == 105:
                logger.info('添加AD用户' + base_dn)
                return True
            else:
                logger.error('添加用户失败: ' + json.dumps(result))
                return False

    def delete(self, dn):
        try:
            result = self.cli.delete_s(dn)
        except Exception as e:
            logger.error('删除' + dn + '失败:' + str(e))
            return False
        else:
            if result[0] == ldap.RES_DELETE:
                logger.info('删除' + dn + '成功')
                return True
            else:
                logger.error('删除用户失败: {}, {}'.format(dn, json.dumps(result)))
                return False

    def exists(self, dn):
        try:
            res = self.cli.search_s(dn, ldap.SCOPE_SUBTREE)
            if res:
                return True
            else:
                return False
        except ldap.NO_SUCH_OBJECT:
            return False

    def search(self, base_dn, filterstr):
        try:
            res = self.cli.search_s(base_dn, ldap.SCOPE_SUBTREE, filterstr)
            return res
        except:
            return []

    def get_last_gid(self):
        try:
            last_gid = int(
                self.cli.search_s('ou=last_gid,dc=weiwen,dc=com', ldap.SCOPE_SUBTREE)[0][1]['description'][0].decode())
        except:
            try:
                self.cli.add_s('ou=last_gid,dc=weiwen,dc=com', [('objectclass', [b'top', b'organizationalUnit']),
                                                                ('ou', [b'last_gid']),
                                                                ('description', [b'888'])])
                last_gid = 888
            except:
                self.cli.modify_s('ou=last_gid,dc=weiwen,dc=com', [
                    (ldap.MOD_ADD, 'description', str(888).encode())])
                last_gid = 888
        mod_gid = last_gid + 1
        self.cli.modify_s('ou=last_gid,dc=weiwen,dc=com',
                          [(ldap.MOD_DELETE, 'description', str(last_gid).encode()),
                           (ldap.MOD_ADD, 'description', str(mod_gid).encode())])
        return str(mod_gid)

    def get_last_uid(self):
        try:
            last_uid = int(
                self.cli.search_s('ou=last_uid,dc=weiwen,dc=com', ldap.SCOPE_SUBTREE)[0][1]['description'][0].decode())
        except:
            try:
                self.cli.add_s('ou=last_uid,dc=weiwen,dc=com', [('objectclass', [b'top', b'organizationalUnit']),
                                                                ('ou', [b'last_uid']),
                                                                ('description', [b'1888'])])
                last_uid = 1888
            except:
                self.cli.modify_s('ou=last_uid,dc=weiwen,dc=com', [
                    (ldap.MOD_ADD, 'description', str(1888).encode())])
                last_uid = 1888
        mod_uid = last_uid + 1
        self.cli.modify_s('ou=last_uid,dc=weiwen,dc=com',
                          [(ldap.MOD_DELETE, 'description', str(last_uid).encode()),
                           (ldap.MOD_ADD, 'description', str(mod_uid).encode())])
        return str(mod_uid)


if __name__ == "__main__":
    cli = LDAP_Client()
    # cli.add_group('cn=default,cn=rere2,cn=adasdad,dc=weiwen,dc=com')
    cli.add_user('cn=wwwwwqq,cn=rere2,cn=adasdad,dc=weiwen,dc=com', '199812', '986940788@qq.com')
    # cli.add_department('ou=rtrttr,ou=ioioio,dc=weiwen,dc=com')
