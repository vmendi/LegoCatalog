# Extrae todas las partes que han sido pesadas alguna vez, añadiendo el numero de veces que ha sido pesada
# y el numero de clusters que ha creado.
# Ultima linea es el filtro por rango de peso
select *
from
	parts
join 
	(select part_number, count(part_number) as number_of_weighings from weighings group by part_number) as weighings_summary
on weighings_summary.part_number = parts.number
join
	(select part_number, count(part_number) as number_of_clusters, avg(mean_weight) as mean_clusters_weight from weighings_clusters group by part_number) as clusters_summary
on clusters_summary.part_number = parts.number
where mean_clusters_weight > 0.76 and mean_clusters_weight < 0.84;

# Determinar el alejamiento maximo entre moldes de la misma pieza. Si el maximo y el minimo molde estan alejados mas
# del 10% en peso => error
select 	part_number, 
		count(part_number) as number_of_clusters, 
		avg(mean_weight), min(mean_weight), max(mean_weight),
		100 * (max(mean_weight) - min(mean_weight)) / min(mean_weight) as percent_deviation,
		(100 * (max(mean_weight) - min(mean_weight)) / min(mean_weight)) > 10 as deviation_error
from weighings_clusters group by part_number;
