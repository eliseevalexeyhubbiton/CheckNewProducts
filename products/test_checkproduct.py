import unittest
from checkproduct import CheckProduct


class TestCaseCheckProduct(unittest.TestCase):

    def test_url_remove(self):
        url_test = "https://poddomen.super-site.life/subcategory/page&list=3&view=True"
        check = CheckProduct()
        check.url_add(url=url_test)
        self.assertEqual(True, check.url_remove(url=url_test))

    def test_get_count_products(self):
        page_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
            <div class="plp-load-more-container">
                <div class="row-flex">
                    <div class="col-s-24">
                        <span class="plp-counter">
                            Viewed <span class=js-plpLoadedProductsCounter>60</span> of 274 products
                        </span>
                    </div>
                </div>
            </div>
        </body>
        </html>        
        """
        xpath = "/html/body/div/div/div/span/text()"
        check = CheckProduct()
        check.set_xpath_count_products(xpath=xpath)
        self.assertEqual(274, check.get_count_products(res_text=page_html))


if __name__ == '__main__':
    unittest.main()
