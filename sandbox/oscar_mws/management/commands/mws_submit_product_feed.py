from optparse import make_option

from django.db.models import get_model
from django.core.management.base import NoArgsCommand

from oscar_mws.feeds.gateway import submit_product_feed
from oscar_mws.models import MerchantAccount

Product = get_model('catalogue', 'Product')


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help=('Do not submit the product feed put print the generated '
                  'XML to stdout.')
        ),
        make_option(
            '--seller-id',
            dest='seller_id',
            help=('Seller ID used to submit the product feed')
        ),
    )

    def handle_noargs(self, **options):
        # get all products without a ASIN assigned
        products = Product.objects.all()

        merchant_id = options.get('seller_id')
        merchant = MerchantAccount.objects.filter(
            seller_id=merchant_id).first()
        if not merchant:
            raise Exception('Merchant doesn\'t exists')

        marketplaces = merchant.marketplaces.all()
        if options.get('dry_run'):
            submit_product_feed(products, marketplaces, dry_run=True)
            return

        submission = submit_product_feed(products, marketplaces)
        print "Submitted as ID #{0}".format(submission.submission_id)
