import context
import os, sys, json
import unittest
#sys.path.append('../../common/src')
import bad_fits

class CommonBadFitsTest(unittest.TestCase):
    def test_good_moc(self):
        filename = 'bad_fits_test_files/orion.fits'
        message = bad_fits.bad_moc_file(filename)
#        print(filename, message)
        self.assertIsNone(message)

    def test_bad_mocorder(self):
        filename = 'bad_fits_test_files/orion29.fits'
        message = bad_fits.bad_moc_file(filename)
#        print(filename, message)
        self.assertIn('Bad MOCORDER', message)
        
    def test_not_fits(self):
        filename = 'bad_fits_test_files/gbpusd.png'
        message = bad_fits.bad_moc_file(filename)
#        print(filename, message)
        self.assertIn('Cannot open as a FITS file', message)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
