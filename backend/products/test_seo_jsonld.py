from django.test import SimpleTestCase

from products.templatetags.seo_jsonld import _jsonld_script


class JsonLdScriptTests(SimpleTestCase):
    def test_json_ld_escapes_script_markup_in_untrusted_text(self):
        script = str(_jsonld_script({"name": "</script><script>alert(1)</script>"}))

        self.assertIn('type="application/ld+json"', script)
        self.assertEqual(script.count("</script>"), 1)
        self.assertIn(r"\u003C/script\u003E\u003Cscript\u003E", script)
