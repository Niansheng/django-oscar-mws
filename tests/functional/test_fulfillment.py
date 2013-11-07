import httpretty

from dateutil.parser import parse as du_parse

from django.test import TestCase
from django.db.models import get_model

from oscar.test.factories import create_order

from oscar_mws.test import mixins, factories
from oscar_mws.fulfillment.gateway import update_fulfillment_order

ShippingEvent = get_model('order', 'ShippingEvent')
ShippingEventType = get_model('order', 'ShippingEventType')

ShipmentPackage = get_model('oscar_mws', 'ShipmentPackage')
FulfillmentOrder = get_model('oscar_mws', 'FulfillmentOrder')
FulfillmentShipment = get_model('oscar_mws', 'FulfillmentShipment')


class TestCreateFulfillmentOrder(mixins.DataLoaderMixin, TestCase):

    @httpretty.activate
    def test_creates_shipments_for_single_address(self):
        httpretty.register_uri(
            httpretty.POST,
            'https://mws.amazonservices.com/FulfillmentOutboundShipment/2010-10-01',
            body=self.load_data('create_fulfillment_order_response.xml'),
        )


class TestUpdatingFulfillmentOrders(mixins.DataLoaderMixin, TestCase):

    def setUp(self):
        super(TestUpdatingFulfillmentOrders, self).setUp()
        self.order = factories.FulfillmentOrderFactory(
            fulfillment_id='1000012345', status='SUBMITTED')

    @httpretty.activate
    def test_updates_a_single_order_status(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://mws.amazonservices.com/FulfillmentOutboundShipment/2010-10-01',
            responses=[httpretty.Response(
                self.load_data('get_fulfillment_order_response.xml'),
            )],
        )
        order = update_fulfillment_order(self.order)
        self.assertEquals(order.status, order.COMPLETE)

        shipments = FulfillmentShipment.objects.all()
        self.assertEquals(len(shipments), 1)
        self.assertEquals(shipments[0].status, 'SHIPPED')
        self.assertEquals(shipments[0].shipment_events.count(), 1)

        self.assertEquals(shipments[0].packages.count(), 1)
        package = shipments[0].packages.all()[0]
        self.assertEquals(package.package_number, 2341234)
        self.assertEquals(package.carrier_code, 'Magic Parcels')
        self.assertEquals(package.tracking_number, 'MPT_1234')

    @httpretty.activate
    def test_updates_an_order_without_shipment_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://mws.amazonservices.com/FulfillmentOutboundShipment/2010-10-01',
            responses=[httpretty.Response(
                self.load_data(
                    'get_fulfillment_order_response_without_shipments.xml'))],
        )
        order = update_fulfillment_order(self.order)
        self.assertEquals(order.status, order.PLANNING)
        self.assertEquals(FulfillmentShipment.objects.count(), 0)


class TestGetFulfillmentOrder(mixins.DataLoaderMixin, TestCase):

    @httpretty.activate
    def test_parses_the_response_correctly(self):
        xml_data = self.load_data('get_fulfillment_order_response.xml')
        httpretty.register_uri(
            httpretty.GET,
            'https://mws.amazonservices.com/FulfillmentOutboundShipment/2010-10-01',
            body=xml_data,
        )

        basket = factories.BasketFactory()
        basket.add_product(factories.ProductFactory())
        order = create_order(basket=basket)

        update_fulfillment_order(
            factories.FulfillmentOrderFactory(order=order)
        )

        fulfillment_order = FulfillmentOrder.objects.all()[0]
        self.assertEquals(FulfillmentOrder.objects.count(), 1)
        self.assertEquals(fulfillment_order.status, 'COMPLETE')

        shipments = FulfillmentShipment.objects.all()
        self.assertEquals(len(shipments), 1)

        expected = {
            'Dkw.3ko298': {
                'shipment_id': 'Dkw.3ko298',
                'status': 'SHIPPED',
                'fulfillment_center_id': 'FCID01',
                'date_shipped': du_parse('2013-10-29T00:50:03Z'),
                'date_estimated_arrival': du_parse('2013-10-30T23:59:59Z'),
            },
        }
        for shipment in shipments:
            for attr, value in expected[shipment.shipment_id].iteritems():
                self.assertEquals(getattr(shipment, attr), value)

        packages = ShipmentPackage.objects.all()
        self.assertEquals(len(packages), 1)

        self.assertEquals(packages[0].tracking_number, 'MPT_1234')
        self.assertEquals(packages[0].carrier_code, 'Magic Parcels')

        shipping_events = ShippingEvent.objects.all()
        self.assertEquals(len(shipping_events), 1)

        self.assertItemsEqual(
            [s.notes for s in shipping_events],
            ['* Shipped package via Magic Parcels with tracking number MPT_1234']
        )
