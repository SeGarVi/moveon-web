-- View: public.moveon_routestation

-- DROP VIEW public.moveon_routestation;

CREATE OR REPLACE VIEW public.moveon_routestation AS 
 SELECT moveon_station.node_ptr_id,
    moveon_station.stop_node_id,
    moveon_station.code,
    moveon_station.name,
    moveon_station.available,
    moveon_station.adapted,
    moveon_station.shelter,
    moveon_station.bench,
    moveon_stretch.route_id,
    moveon_routepoint."order"
   FROM moveon_station
     LEFT JOIN moveon_routepoint ON moveon_station.node_ptr_id = moveon_routepoint.node_id
     JOIN moveon_stretch ON moveon_routepoint.stretch_id = moveon_stretch.id
  WHERE moveon_stretch.signature = ''::text;

ALTER TABLE public.moveon_routestation
  OWNER TO moveon;
