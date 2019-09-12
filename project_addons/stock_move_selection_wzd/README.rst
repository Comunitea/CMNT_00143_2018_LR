Actualización de Inventario
===========================

1º Instarucciones para actualizar
--------------------------------------------------------------

Desinstalar stock_picking_custom_lr
Dará un fallo al desinstalar ( o no) pero queda marcado para desinstalar.

2º Actualizar  git
------------------

Lo de siempre

3º Ejecutar las queries
-----------------------

delete from ir_ui_view where arch_db like '%manual_pick%';
delete from ir_ui_view where arch_db like '%shipping_type%';

4º Arrancar con ...
----------------------

-u stock_move_selection_wzd,shipping_type,stock_picking_group
