CREATE TABLE domain_error (
	id serial4 NOT NULL,
	dominio varchar(1000) NULL,
	CONSTRAINT domain_error_pkey PRIMARY KEY (id)
);
CREATE TABLE ongs (
	id serial4 NOT NULL,
	dominio varchar(1000) NULL,
	prov_dominio_iana_id int4 NULL,
	pais varchar(2) NOT NULL,
	CONSTRAINT ongs_pkey PRIMARY KEY (id)
);
CREATE TABLE prov_hosting (
	id serial4 NOT NULL,
	pais varchar(1000) NULL,
	ciudad varchar(1000) NULL,
	organization varchar(1000) NULL,
	isp varchar(1000) NULL,
	asn varchar(1000) NULL,
	CONSTRAINT prov_hosting_pkey PRIMARY KEY (id)
);
CREATE TABLE servicio_u (
	servicio varchar(1000) NULL,
	n_version varchar(1000) NULL,
	id serial4 NOT NULL,
	cpe varchar(300) NULL,
	CONSTRAINT servicio_u_pkey PRIMARY KEY (id)
);
CREATE TABLE cname (
	id serial4 NOT NULL,
	cname varchar(1000) NULL,
	dominio int4 NOT NULL,
	CONSTRAINT cname_pkey PRIMARY KEY (id),
	CONSTRAINT cname_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE ip (
	id serial4 NOT NULL,
	ip varchar(1000) NULL,
	ip_ports varchar(1000) NULL,
	dominio int4 NOT NULL,
	type_ip bool NOT NULL,
	prov_hosting int4 NOT NULL,
	CONSTRAINT ip_pkey PRIMARY KEY (id),
	CONSTRAINT ip_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT ip_prov_hosting_fkey FOREIGN KEY (prov_hosting) REFERENCES prov_hosting(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE ip_error (
	id serial4 NOT NULL,
	ip varchar(100) NOT NULL,
	dominio int4 NOT NULL,
	type_ip bool NOT NULL,
	CONSTRAINT ip_error_pkey PRIMARY KEY (id),
	CONSTRAINT ip_error_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE mx (
	id serial4 NOT NULL,
	mx varchar(1000) NULL,
	dominio int4 NOT NULL,
	CONSTRAINT mx_pkey PRIMARY KEY (id),
	CONSTRAINT mx_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE ns (
	id serial4 NOT NULL,
	ns varchar(1000) NULL,
	dominio int4 NOT NULL,
	CONSTRAINT ns_pkey PRIMARY KEY (id),
	CONSTRAINT ns_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE servicio_ip_u (
	ip int4 NULL,
	servicio int4 NULL,
	id serial4 NOT NULL,
	CONSTRAINT servicio_ip_u_pkey PRIMARY KEY (id),
	CONSTRAINT servicio_ip_ip_fkey FOREIGN KEY (ip) REFERENCES ip(id),
	CONSTRAINT servicio_ip_servicio_fkey FOREIGN KEY (servicio) REFERENCES servicio_u(id)
);
CREATE TABLE servicio_nmap (
	id serial4 NOT NULL,
	ip int4 NOT NULL,
	puerto int4 NOT NULL,
	protocolo varchar(100) NOT NULL,
	estado varchar(100) NOT NULL,
	servicio varchar(100) NOT NULL,
	CONSTRAINT servicio_nmap_pkey PRIMARY KEY (id),
	CONSTRAINT servicio_nmap_ip_fkey FOREIGN KEY (ip) REFERENCES ip(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE soa (
	id serial4 NOT NULL,
	soa varchar(1000) NULL,
	dominio int4 NOT NULL,
	CONSTRAINT soa_pkey PRIMARY KEY (id),
	CONSTRAINT soa_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE txt (
	id serial4 NOT NULL,
	txt varchar(1000) NULL,
	dominio int4 NOT NULL,
	CONSTRAINT txt_pkey PRIMARY KEY (id),
	CONSTRAINT txt_dominio_fkey FOREIGN KEY (dominio) REFERENCES ongs(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE vulnerabilidad_int (
	id serial4 NOT NULL,
	cve varchar(100) NOT NULL,
	score float8 NOT NULL,
	servicio_u int4 NOT NULL,
	av int4 NOT NULL,
	ac int4 NOT NULL,
	au int4 NOT NULL,
	c int4 NOT NULL,
	i int4 NOT NULL,
	a int4 NOT NULL,
	CONSTRAINT vulnerabilidad_int_pkey PRIMARY KEY (id),
	CONSTRAINT vulnerabilidad_int_servicio_u_fkey FOREIGN KEY (servicio_u) REFERENCES servicio_u(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE vulnerabilidad_nvd (
	id serial4 NOT NULL,
	cve varchar(100) NOT NULL,
	score float8 NOT NULL,
	servicio_u int4 NOT NULL,
	access_vector varchar(1) NOT NULL,
	access_complexity varchar(1) NOT NULL,
	authentication_requirement varchar(1) NOT NULL,
	confidentiality_impact varchar(1) NOT NULL,
	integrity_impact varchar(1) NOT NULL,
	availability_impact varchar(1) NOT NULL,
	CONSTRAINT vulnerabilidad_nvd_pkey PRIMARY KEY (id),
	CONSTRAINT vulnerabilidad_nvd_servicio_u_fkey FOREIGN KEY (servicio_u) REFERENCES servicio_u(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE ip_error_mx (
	id serial4 NOT NULL,
	ip varchar(100) NOT NULL,
	dominio int4 NOT NULL,
	type_ip bool NOT NULL,
	CONSTRAINT ip_error_mx_pkey PRIMARY KEY (id),
	CONSTRAINT ip_error_mx_dominio_fkey FOREIGN KEY (dominio) REFERENCES mx(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE ip_mx (
	id serial4 NOT NULL,
	mx int4 NOT NULL,
	ip_mx varchar(1000) NULL,
	ip_ports varchar(10000) NULL,
	type_ip bool NOT NULL,
	prov_hosting int4 NOT NULL,
	CONSTRAINT ip_mx_pkey PRIMARY KEY (id),
	CONSTRAINT ip_mx_mx_fkey FOREIGN KEY (mx) REFERENCES mx(id) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT ip_mx_prov_hosting_fkey FOREIGN KEY (prov_hosting) REFERENCES prov_hosting(id) DEFERRABLE INITIALLY DEFERRED
);
