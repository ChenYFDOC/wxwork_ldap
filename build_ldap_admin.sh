#!/bin/bash -e
sudo docker run -p 389:389 --env LDAP_ORGANISATION="WeiWen" --env LDAP_TLS=flase --env LDAP_DOMAIN="weiwen.com" --env LDAP_ADMIN_PASSWORD="199812" --name ldap-service --hostname ldap-service --detach osixia/openldap:1.1.8
sudo docker run --name phpldapadmin-service --hostname phpldapadmin-service --link ldap-service:ldap-host --env PHPLDAPADMIN_LDAP_HOSTS=ldap-host --env PHPLDAPADMIN_HTTPS=false --detach osixia/phpldapadmin:0.9.0

PHPLDAP_IP=$(sudo docker inspect -f "{{ .NetworkSettings.IPAddress }}" phpldapadmin-service)

echo "Go to: http://$PHPLDAP_IP"
echo "Login DN: cn=admin,dc=weiwen,dc=com"
echo "Password: 199812"