# docker build --tag mikahpinegar/azurefunctionsimage:v1.0.0 .
# docker network create azure-functions

# docker run -d -p 1111:5432 --net azure-functions dbregistry.azurecr.io/crowndb-snapshot:08.08.2022

# docker run -d -p 2222:5432 --net azure-functions dbregistry.azurecr.io/shadowdb-snapshot:08.08.2022

docker run  -p 8080:80 `
            -e FUNCTIONS_WORKER_RUNTIME=python `
            -e AUTH0_AUDIENCE=https://precision-sustaibale-ag/tech-dashboard `
            -e AUTH0_DOMAIN=psa-tech-dashboard.auth0.com `
            -e AUTH0_PAYLOAD="{\"client_id\":\"RKkiHSDtTGQWijgy7q7Pi7sheonzWZke\",\"client_secret\":\"pzoI_Zwp4i-PSlb0lHVOZTyl8zZ8iQmuzJ8GNfR4pY1Ttr1PgXPK3Bbk-LdRXyf9\",\"audience\":\"https:\/\/psa-tech-dashboard.auth0.com\/api\/v2\/\",\"grant_type\":\"client_credentials\"}" `
            -e LIVE_SHADOW_DBNAME=shadowdb `
            -e LIVE_CROWN_DBNAME=crowndb `
            -e LIVE_HOST=onfarm-dbs.postgres.database.azure.com `
            -e LIVE_PASSWORD=a95cbcb52871_260a_cbe4_312d_c3519e82 `
            -e LIVE_SSLMODE=require `
            -e LIVE_USER=python_api_user@onfarm-dbs `
            -e LOCAL_PROD_HOST=crown_testbed `
            -e LOCAL_PROD_DBNAME=crowndb `
            -e LOCAL_PROD_USER=postgres `
            -e LOCAL_PROD_PASSWORD=asecretpassword `
            -e LOCAL_PROD_SSLMODE=disable `
            -e LOCAL_PROD_PORT=1111 `
            -e LOCAL_SHADOW_HOST=shadow_testbed `
            -e LOCAL_SHADOW_DBNAME=shadowdb `
            -e LOCAL_SHADOW_USER=postgres `
            -e LOCAL_SHADOW_PASSWORD=asecretpassword `
            -e LOCAL_SHADOW_SSLMODE=disable `
            -e LOCAL_SHADOW_PORT=2222 `
            -e MYSQL_DBNAME=tech-dashboard `
            -e MYSQL_HOST=new-tech-dashboard.mysql.database.azure.com `
            -e MYSQL_PASSWORD=3ad629a4c037=a8db=bed4=f9e8=7fee785e `
            -e MYSQL_SSLMODE=require `
            -e MYSQL_USER=python_api_user@new-tech-dashboard `
            -e EXPIRED_USER_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlF6Z3pSRVpCUkVRM1EwTkdRekE0UlRGRU9EZzBPVUV6T0RGRFJUQXlPVGRCUTBNMU5VTTFOUSJ9.eyJpc3MiOiJodHRwczovL3BzYS10ZWNoLWRhc2hib2FyZC5hdXRoMC5jb20vIiwic3ViIjoiZ2l0aHVifDU1OTk1MjQxIiwiYXVkIjpbImh0dHBzOi8vcHJlY2lzaW9uLXN1c3RhaWJhbGUtYWcvdGVjaC1kYXNoYm9hcmQiLCJodHRwczovL3BzYS10ZWNoLWRhc2hib2FyZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjUxMDgwMTA4LCJleHAiOjE2NTExNjY1MDgsImF6cCI6Imp3OE1wVVJDaWl5RTNUcWpZcml3R1V0UnZxOWhFSWdEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbXX0.sj-I-JFLa4kVOYqGXMCLsLJ3s7v8ga1VfwI6apbtPEhHEndQ2Piq4w9GeWCa8vk7uWeMxmbceW67snex2VduWi9EKaFYaXLfw6YhOp3Phz0U0JRAQ9QiCuMI6brY4PIpMdpkqU7azM1GOP0rHA5LFHsxHcfF3C4LRh-heZCyraxTV7h-iWNlHqM_QxVsMvIejv1KOm6AsPY42Bbl1GlCZKRJlc0i---8MFIzBWYCddk08uCtq30at5gu7_x6_VbRyWcUsxbIKhHWJVtr4OG9apbjodkMQKds6b8BbkbipwEGeEQk7EO1HRajXEGzMsx9HmR4jgcVkqqR04Thtzcn_w `
            -e USER_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlF6Z3pSRVpCUkVRM1EwTkdRekE0UlRGRU9EZzBPVUV6T0RGRFJUQXlPVGRCUTBNMU5VTTFOUSJ9.eyJpc3MiOiJodHRwczovL3BzYS10ZWNoLWRhc2hib2FyZC5hdXRoMC5jb20vIiwic3ViIjoiZ2l0aHVifDU1OTk1MjQxIiwiYXVkIjpbImh0dHBzOi8vcHJlY2lzaW9uLXN1c3RhaWJhbGUtYWcvdGVjaC1kYXNoYm9hcmQiLCJodHRwczovL3BzYS10ZWNoLWRhc2hib2FyZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjU0NTM4ODM1LCJleHAiOjE2NTQ2MjUyMzUsImF6cCI6Imp3OE1wVVJDaWl5RTNUcWpZcml3R1V0UnZxOWhFSWdEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbXX0.Z_ZrcUnIWcWe4GJoEf4LuAk9j3q_a0zBW5Qf8drNESXQMeGAP8P3ei-mQZDy-QkowBYH6ty_rO2XkIPgNGdpNJD_fgfJl_pNdRMs2TV5ko521omWzsPqvacI6JfewfSRy1EfnDoHttpeFpdPvvG5qRc01uvvBcR3HxsKjbdOa4-uX7e9zFtXXpXB4iQzs5duNu26FN1b_GZxb_NxvS2lMDumBhOTjior4lMH8gPOn82TbUn7-MCK8Wp8vzCWpDk_PUA44ZWqvPZ4Sn04IyzDm_TICaXNs_XEHmNnQfJ3TVSIEANEZEWW7HZotzVrC6cBAyjYJDKp9fa4QwkDMuTOtQ `
            -e WEEDS3D_SAS_TOKEN="?sv=2020-08-04&ss=bfqt&srt=sco&sp=ltfx&se=2025-06-02T00:46:10Z&st=2022-06-01T16:46:10Z&spr=https,http&sig=SlTao%2FNncHSSYtFLPS8Q3wN6RkiqkY2sHH%2FDoQ6l8ic%3D" `
            --net azure-functions `
            -it mikahpinegar/azurefunctionsimage:v1.0.0