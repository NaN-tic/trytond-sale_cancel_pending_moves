# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not
from trytond.transaction import Transaction


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    pending_moves = fields.Function(fields.Many2Many('stock.move', None, None,
            'Pending Moves'), 'get_pending_moves', setter='set_pending_moves')

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        cls._buttons.update({
                'cancel_pending_moves': {
                    'invisible': Not(Bool(Eval('pending_moves'))),
                    },
                })

    @classmethod
    @ModelView.button
    def cancel_pending_moves(cls, sales):
        pool = Pool()
        StockMove = pool.get('stock.move')
        ShipmentOut = pool.get('stock.shipment.out')
        ShipmentOutReturn = pool.get('stock.shipment.out.return')
        HandleShipmentException = pool.get(
            'sale.handle.shipment.exception', type='wizard')

        for sale in sales:
            pending_moves = sale.pending_moves
            StockMove.cancel(pending_moves)

            with Transaction().set_context(active_model=cls.__name__,
                    active_ids=[sale.id], active_id=sale.id):
                session_id, _, _ = HandleShipmentException.create()
                handle_shipment_exception = HandleShipmentException(session_id)
                handle_shipment_exception.ask.recreate_moves = []
                handle_shipment_exception.ask.domain_moves = pending_moves
                handle_shipment_exception.transition_handle()
                HandleShipmentException.delete(session_id)

            shipments = []
            for shipment in sale.shipments:
                if not any([x.state != 'cancelled' for x in shipment.moves]):
                    shipments.append(shipment)
            if shipments:
                ShipmentOut.cancel(shipments)

            shipments = []
            for shipment in sale.shipment_returns:
                if not any([x.state != 'cancelled' for x in shipment.moves]):
                    shipments.append(shipment)
            if shipments:
                ShipmentOutReturn.cancel(shipments)

    @classmethod
    def get_pending_moves(cls, sales, name=None):
        result = dict((s.id, []) for s in sales)

        for sale in sales:
            for line in sale.lines:
                result[sale.id].extend([m.id for m in line.pending_moves])
        return result

    @classmethod
    def set_pending_moves(cls, purchases, name, value):
        pass


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'
    pending_moves = fields.Function(fields.Many2Many('stock.move', None, None,
            'Pending Moves'), 'get_pending_moves')

    @classmethod
    def get_pending_moves(cls, lines, name):
        pending_moves = {}
        for line in lines:
            moves = []
            skip = set(line.moves_ignored + line.moves_recreated)
            for move in line.moves:
                if move.state not in ('cancelled', 'done') and move not in skip:
                    moves.append(move.id)
            pending_moves[line.id] = moves

        return pending_moves
