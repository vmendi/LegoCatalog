DROP TABLE IF EXISTS categories;
CREATE TABLE categories
(
	category_id INT NOT NULL,
	category_name VARCHAR(128) NOT NULL,
	
	PRIMARY KEY (category_id)
);

DROP TABLE IF EXISTS colors;
CREATE TABLE colors
(
	color_id INT NOT NULL,
	color_name VARCHAR(256) NOT NULL,
	rgb varchar(16) NOT NULL,
	type varchar(32) NOT NULL,
	parts INT NOT NULL,
	in_sets	INT NOT NULL,
	wanted INT NOT NULL,
	for_sale INT NOT NULL,
	year_from INT NOT NULL,
	year_to INT NOT NULL,
	
	PRIMARY KEY (color_id)
);

DROP TABLE IF EXISTS parts;
CREATE TABLE parts 
(
	category_id INT NOT NULL,
	category_name varchar(128) NOT NULL,
	number VARCHAR(32) NOT NULL,
	name VARCHAR(256) NOT NULL,
	weight DOUBLE NOT NULL DEFAULT 0,
	dimensions varchar(32),
	
	PRIMARY KEY(number)
);

DROP TABLE IF EXISTS codes;
CREATE TABLE codes
(
	part_number INT NOT NULL,
	color_name varchar(256) NOT NULL,
	code INT NOT NULL,
	
	KEY (part_number)
);

DROP TABLE IF EXISTS sets;
CREATE TABLE sets
(
	category_id INT NOT NULL,
	category_name VARCHAR(128) NOT NULL,
	number VARCHAR(32) NOT NULL,
	name VARCHAR(256) NOT NULL,
	year INT NOT NULL,
	weigth DOUBLE NOT NULL DEFAULT 0,
	dimensions VARCHAR(32),
	
	PRIMARY KEY(number)
);

DROP TABLE IF EXISTS inventories;
CREATE TABLE inventories
(
	set_number VARCHAR(32) NOT NULL,
	part_number VARCHAR(32) NOT NULL,
	color_id INT NOT NULL,
	qty INT NOT NULL,
	match_id INT NOT NULL,
	type CHAR NOT NULL,
	extra CHAR NOT NULL,
	counterpart CHAR NOT NULL,
	
	KEY (part_number),
	KEY (set_number),
	KEY(color_id)
);

DROP TABLE IF EXISTS weighings;
CREATE TABLE weighings
(
  weighing_id int NOT NULL AUTO_INCREMENT,
  part_number varchar(32) NOT NULL,
  color_id int(11) NOT NULL,
  weight DECIMAL(15, 5) NOT NULL,
  threshold DECIMAL(15, 5) NOT NULL,
  created_at_pst datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  weighing_cluster_id int NOT NULL,
  cluster_threshold DECIMAL(15, 5) NOT NULL,
  	
  PRIMARY KEY(weighing_id),
  KEY (part_number)
);

DROP TABLE IF EXISTS weighings_clusters;
CREATE TABLE weighings_clusters
(
  weighing_cluster_id int NOT NULL AUTO_INCREMENT,
  part_number varchar(32) NOT NULL,
  mean_weight DECIMAL(15, 5) NOT NULL,
  weighings_count int NOT NULL,
  
  PRIMARY KEY(weighing_cluster_id),
  KEY(part_number),
  KEY(mean_weight)
);

# Download these files from http://www.bricklink.com/catalogDownload.asp
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Categories.txt' INTO TABLE categories LINES TERMINATED BY '\r\n' IGNORE 2 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Colors.txt' INTO TABLE colors LINES TERMINATED BY '\r\n' IGNORE 2 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Parts.txt' INTO TABLE parts LINES TERMINATED BY '\r\n' IGNORE 3 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Codes.txt' INTO TABLE codes LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Sets.txt' INTO TABLE sets LINES TERMINATED BY '\r\n' IGNORE 3 LINES;

	
#----------------------------------------------------------------------------------------
# Empiezo de nuevo, creo que lo mejor es tomar la lista filtrada como base para todas las
# demas queries, especialmente la de peso que es la que mas nos interesa ahora mismo, 
# dejo lo de arriba como referencia

# Vista filtrada que quita categorias que no nos gustan y piezas que no aparecen desde X year
drop table if exists filtered_parts;
create table filtered_parts (PRIMARY KEY(number), KEY(category_id)) as
select parts.category_id, parts.category_name, parts.number, parts.name, parts.weight, parts.dimensions 
	from parts
	join categories on parts.category_id = categories.category_id
	join inventories on inventories.part_number = parts.number
	join sets on inventories.set_number = sets.number 
where categories.category_name not like '%duplo%'   # Bebes
and categories.category_name not like '%sticker%'   # Papeles
and categories.category_name not like '%minifig%'   # Mejor prefiltrarlas a mano
and categories.category_name not like '%modulex%'   # Raras
and categories.category_name not like '%jumbo%'     # Bebes
and categories.category_name not like '%primo%'     # Bebes
and categories.category_name not like '%paper%'     # Papeles
and categories.category_name not like '%belville%'	# Ninyas, muy raras
and categories.category_name not like '%electric%'	# Creo que no habra muchas y sera facil prefiltrarlas
and categories.category_name not like '%clikits%'   # Son unas minifigs y piezas raras (estrella hexagonal?!) de ninya
and categories.category_name not like '%foam%'      # Piezas de foam raras
and categories.category_name not like '%galidor%'   # Muy raras, parecen como que las hicieron para McDonalds
and categories.category_name not like '%bionicle%'  # En principio no queremos bionicles
and categories.category_name not like '%scala%'	    # Antiguo and for girls
and categories.category_name not like '%large figure part%' # Piezas como de figures raras, algunas de Nestle
and categories.category_name not like '%fabuland%'	# Acabo en 1989 y son para bebes
and parts.name not like '%duplo%'                   # Despues de filtrar por el nombre de la categoria, aun quedan algunas piezas
and parts.name not like '%belville%'                # Despues de filtrar por el nombre de la categoria, aun quedan algunas piezas
and parts.category_name not like '%decorated%'      # OPCIONAL! Las piezas decoradas en general pesan lo mismo que la base. De ~14,000 a 5700!
and sets.year >= 1990 and inventories.type = "P"
group by parts.weight, parts.category_id, parts.category_name, parts.number, parts.name, parts.dimensions  # Agrupadas por peso primero, 
																										   # para que puedas ver repeticion 
																										   # y distancia entre pesos
;

# Cuantas piezas en la vista filtrada?
SELECT count(*) from filtered_parts;

# Cuantas piezas pesan lo mismo?
select weight, count(*) 
	from filtered_parts
group by weight order by weight asc;

# Ver todas las que pesan lo mismo de un peso concreto, para ver que pinta tienen
select *
	from filtered_parts
where weight = 1.2;

# La query para filtrar por peso con threshold
SELECT *
	FROM filtered_parts
WHERE weight >= 2.32 - 0.01 AND weight <= 2.32 + 0.01;

# Numero de piezas por categoria
select count(*) as parts_count_per_category, category_name
	from filtered_parts
group by category_name
order by parts_count_per_category desc;

# Cuantos tipos de piezas a partir de un año pero que aparezcan en la lista filtrada?
select SUM(distinct(inventories.part_number)
	from inventories
	join sets on inventories.set_number = sets.number 
	join filtered_parts on filtered_parts.number = inventories.part_number
where sets.year >= 2006 and type = "P";


#----------------------------------------------------------------------------------------
# Ranking segun cantidad de piezas en sets a partir de un anyo. Da una idea de la probabilidad de encontrarnos con una pieza. Solo
# una idea, no conocemos cuantos sets se vendieron de cada.
#
# Esta tabla substituye a filtered_parts
#
drop table if exists filtered_parts_with_qty;
create table filtered_parts_with_qty (PRIMARY KEY (number), KEY(weight)) as
SELECT SUM(inventories.qty) as total_qty, filtered_parts.*, FLOOR(SUM(inventories.qty) * weight) as qty_by_weight
	from inventories 
	join sets on inventories.set_number = sets.number
	join filtered_parts on filtered_parts.number = inventories.part_number
group by filtered_parts.number
order by total_qty desc;

drop table if exists ordering;
create table ordering as
select number, name, category_name, qty_by_weight, weight, CONCAT("http://alpha.bricklink.com/pages/clone/catalogitem.page?P=", number) as url
from filtered_parts_with_qty;

alter table ordering add column ordering VARCHAR(64);

