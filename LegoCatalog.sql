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
	year_to INT NOT NULL
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
	code INT NOT NULL
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
	counterpart CHAR NOT NULL
);

LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Categories.txt' INTO TABLE categories LINES TERMINATED BY '\r\n' IGNORE 2 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Colors.txt' INTO TABLE colors LINES TERMINATED BY '\r\n' IGNORE 2 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Parts.txt' INTO TABLE parts LINES TERMINATED BY '\r\n' IGNORE 3 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Codes.txt' INTO TABLE codes LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
LOAD DATA INFILE '/users/vmendi/Documents/LegoCatalog/data/BrickLink/Sets.txt' INTO TABLE sets LINES TERMINATED BY '\r\n' IGNORE 3 LINES;


# --------------------------------------------------------------------------------------
create or replace view filtered_parts as
select parts.category_id, parts.category_name, parts.number, 
	   parts.name, parts.weight, parts.dimensions from parts
join categories on parts.category_id = categories.category_id
where categories.category_name not like '%duplo%'
and categories.category_name not like '%sticker%'
and categories.category_name not like '%minifig%'
and categories.category_name not like '%modulex%'
and categories.category_name not like '%jumbo%'
;

# Cuantas categorias tenemos?
SELECT distinct category_name from filtered_parts;	# 162

# Cuantos tipos de piezas a partir de un año?
select distinct(inventories.part_number) from inventories 
	join sets on inventories.set_number = sets.number 
	where sets.year >= 2005 and type = "P";

# Piezas agrupadas por color. Cuantas en total ponen en los sets a partir de un año?
SELECT SUM(QTY), inventories.part_number, colors.color_name, parts.name, parts.weight
	from inventories 
	join parts on inventories.part_number = parts.number
	join sets on inventories.set_number = sets.number
	join colors on inventories.color_id = colors.color_id
where sets.year >= 2000 and sets.category_name not like '%duplo%'
group by inventories.part_number, inventories.color_id order by sum(qty) desc;

# Ranking de colores segun cuantas piezas ponen en los sets de ese color.
SELECT SUM(QTY), colors.color_name
	from inventories 
	join sets on inventories.set_number = sets.number
	join colors on inventories.color_id = colors.color_id
where sets.year >= 1990 and sets.category_name not like '%duplo%'
group by inventories.color_id order by sum(qty) desc;

# Cuantas piezas pesan lo mismo?
select weight, count(*) from filtered_parts group by weight order by weight desc;

# Cuantas piezas pesan mas de una cantidad?
select * from filtered_parts where weight > 500;