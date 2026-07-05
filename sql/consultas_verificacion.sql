-- 1. Cuantos registros hay en `fact_prestamos`.
select count(*) as total_fact_prestamos from fact_prestamos;


-- 2. Cuantos registros hay en `etl_errores`.
select count(*) as total_errores from etl_errores;


-- 3. Que errores fueron registrados.
select id_registro, descripcion_error, fecha_error from etl_errores;


-- 4. Cual fue el último estado registrado en `etl_log`.
select estado, fecha_ejecucion from etl_log order by fecha_ejecucion desc limit 1;


-- 5. Total de multas por carrera.
select c.carrera, sum(f.total_multa) as total_multas from fact_prestamos f join dim_carrera c on f.id_carrera = c.id_carrera group by c.carrera order by total_multas desc;


-- 6. Total de multas por categoria de libro.
select l.categoria, sum(f.total_multa) as total_multas from fact_prestamos f join dim_libro l on f.id_libro = l.id_libro group by l.categoria order by total_multas desc;


-- 7. Promedio de dias de prestamo por sede.
select s.sede, avg(f.dias_prestamo) as promedio_dias from fact_prestamos f join dim_sede s on f.id_sede = s.id_sede group by s.sede;


-- 8. Los 5 libros con mayor total de multa.
select l.libro, sum(f.total_multa) as total_multas from fact_prestamos f join dim_libro l on f.id_libro = l.id_libro group by l.libro order by total_multas desc limit 5;


-- 9. Prestamos detallados con fecha, alumno, carrera, libro, categoria, sede y total de multa.
select f.id_prestamo, fe.fecha, a.alumno, c.carrera, l.libro, l.categoria, s.sede, f.total_multa from fact_prestamos f join dim_fecha fe on f.id_fecha = fe.id_fecha
join dim_alumno a on f.id_alumno = a.id_alumno
join dim_carrera c on f.id_carrera = c.id_carrera
join dim_libro l on f.id_libro = l.id_libro
join dim_sede s on f.id_sede = s.id_sede;


-- 10. Conteo de prestamos por sede.
select s.sede, count(*) as total_prestamos from fact_prestamos f
join dim_sede s on f.id_sede = s.id_sede group by s.sede;