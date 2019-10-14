import unittest
from auction.auction import Advertiser
from auction.auction import maximizeGroupRevenueWeighted
from auction.auction import allocateExtended
from auction.auction import maximizeGroupRevenueExtended
from auction.auction import maximizeGroupRevenueUnweighted
from auction.auction import getPrice
from auction.auction import allocateRandom

class MaximizeGroupRevenueWeightedTest(unittest.TestCase):

    def setUp(self):
        self.advertiser_1000_450 = Advertiser(2, 450, {0: 500})
        self.advertiser_1000_250 = Advertiser(2, 250, {0: 500})
        self.advertiser_1000_100 = Advertiser(2, 100, {0: 500})
        self.advertiser_800_250 = Advertiser(4, 250, {0: 200})
        self.advertiser_800_100 = Advertiser(4, 100, {0: 200})
        self.advertiser_600_250 = Advertiser(3, 250, {0: 200})


    def testFirstMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_1000_450, self.advertiser_800_250, self.advertiser_600_250]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(2, value_per_engagement)
        self.assertEqual(1000, value)


    def testSecondMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_1000_250, self.advertiser_800_250, self.advertiser_600_250]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(4, value_per_engagement)
        self.assertEqual(800, value)


    def testThirdMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_1000_100, self.advertiser_800_100, self.advertiser_600_250]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(3, value_per_engagement)
        self.assertEqual(600, value)


class MaximizeGroupRevenueUnweightedTest(unittest.TestCase):

    def setUp(self):
        self.advertiser_4_2000 = Advertiser(4, 2000, {0: 1000})
        self.advertiser_4_800 = Advertiser(4, 800, {0: 1000})
        self.advertiser_4_100 = Advertiser(4, 100, {0: 1000})
        self.advertiser_3_500 = Advertiser(3, 500, {0: 1000})
        self.advertiser_3_200 = Advertiser(3, 200, {0: 1000})
        self.advertiser_2_200 = Advertiser(2, 200, {0: 1000})


    def testFirstMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_4_2000, self.advertiser_3_500, self.advertiser_2_200]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(4, value_per_engagement)
        self.assertEqual(4000, value)


    def testSecondMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_4_800, self.advertiser_3_500, self.advertiser_2_200]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(3, value_per_engagement)
        self.assertEqual(3000, value)


    def testThirdMaximizing(self):
        # arrange
        advertisers_list = [self.advertiser_4_100, self.advertiser_3_200, self.advertiser_2_200]
        # act
        value_per_engagement, value = maximizeGroupRevenueWeighted(advertisers_list)
        # assert
        self.assertEqual(2, value_per_engagement)
        self.assertEqual(2000, value)


class MaximizeGroupRevenueExtendedTest(unittest.TestCase):

    def setUp(self):
        self.a1_1 = Advertiser(1, 200, {'s1': 300, 's2': 80})
        self.a1_2 = Advertiser(1, 200, {'s1': 300, 's2': 100})
        self.a1_3 = Advertiser(2, 200, {'s1': 300, 's2': 100})
        self.a1_4 = Advertiser(2, 200, {'s1': 300, 's2': 100})
        self.a2_1 = Advertiser(2, 200, {'s1': 100, 's2': 300})
        self.a2_2 = Advertiser(2, 200, {'s1': 80, 's2': 300})
        self.a2_3 = Advertiser(2, 200, {'s1': 200, 's2': 100})
        self.a2_4 = Advertiser(2, 200, {'s1': 100, 's2': 100})

    
    def testAllocateOneNonWeighted(self):
        # arrange
        advertisers = [self.a1_1, self.a2_1]
        # act
        value_per_engagement, value = maximizeGroupRevenueExtended(advertisers, False, 1)
        # assert
        self.assertEqual(2, value_per_engagement)
        self.assertEqual(800, value)


    def testAllocateBothNonWeighted(self):
        # arrange
        advertisers = [self.a1_2, self.a2_2]
        # act
        value_per_engagement, value = maximizeGroupRevenueExtended(advertisers, False, 1)
        # assert
        self.assertEqual(1, value_per_engagement)
        self.assertEqual(400, value)


    def testAllocateOneWeighted(self):
        # arrange
        advertisers = [self.a1_3, self.a2_3]
        # act
        value_per_engagement, value = maximizeGroupRevenueExtended(advertisers, False, 1)
        # assert
        self.assertEqual(2, value_per_engagement)
        self.assertEqual(800, value)


    def testAllocateBothWeighted(self):
        # arrange
        advertisers = [self.a1_4, self.a2_4]
        # act
        value_per_engagement, value = maximizeGroupRevenueExtended(advertisers, False, 1)
        # assert
        self.assertEqual(2, value_per_engagement)
        self.assertEqual(400, value)


class AllocateExtendedTest(unittest.TestCase):

    def setUp(self):
        self.a1 = Advertiser(1, 200, {'s1': 300, 's2': 100, 's3': 10})
        self.a2 = Advertiser(2, 150, {'s1': 100, 's2': 300, 's3': 10})
        self.b1 = Advertiser(3, 200, {'s1': 115, 's2': 100, 's3': 60})
        self.b2 = Advertiser(4, 150, {'s1': 100, 's2': 100, 's3': 75})

    
    def testNonWeighted(self):
        # arrange
        advertisers_a = [self.a1, self.a2]
        advertisers_b = [self.b1, self.b2]
        # act
        revenue, _ = allocateExtended(advertisers_a, advertisers_b, 2, 1, 0, 0, False, False, 1)
        # assert
        self.assertAlmostEqual(450, revenue, places=4)


    def testWeighted(self):
        # arrange
        advertisers_a = [self.a1, self.a2]
        advertisers_b = [self.b1, self.b2]
        # act
        revenue, _ = allocateExtended(advertisers_a, advertisers_b, 0, 0, 550, 410, True, False, 1)
        # assert
        self.assertAlmostEqual(450, revenue, places=4)

    
    def testNonWeightedNonTruthful(self):
        # arrange
        advertisers_a = [self.a1, self.a2]
        advertisers_b = [self.b1, self.b2]
        # act
        revenue, _ = allocateExtended(advertisers_a, advertisers_b, 1, 2, 0, 0, False, True, 1)
        # assert
        self.assertAlmostEqual(450, revenue, places=4)


    def testWeightedNonTruthful(self):
        # arrange
        advertisers_a = [self.a1, self.a2]
        advertisers_b = [self.b1, self.b2]
        # act
        revenue, _ = allocateExtended(advertisers_a, advertisers_b, 0, 0, 410, 550, True, True, 1)
        # assert
        self.assertAlmostEqual(450, revenue, places=4)


class GetPriceTest(unittest.TestCase):

    def setUp(self):
        self.advertiser_a = Advertiser(1, 200, {'s1': 300, 's2': 100, 's3': 100})
        self.advertiser_b = Advertiser(1, 200, {'s1': 30, 's2': 10, 's3': 10})
        self.advertisers_a = [self.advertiser_a]
        self.advertisers_b = [self.advertiser_b]


    def testGetPriceWeightedTruthful(self):
        # act
        price_a = getPrice(self.advertiser_a, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, True, False)
        price_b = getPrice(self.advertiser_b, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, True, False)
        # assert
        self.assertAlmostEqual(0.8, price_a, places=4)
        self.assertAlmostEqual(6.0, price_b, places=4)


    def testGetPriceWeightedNonTruthful(self):
        # act
        price_a = getPrice(self.advertiser_a, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, True, True)
        price_b = getPrice(self.advertiser_b, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, True, True)
        # assert
        self.assertAlmostEqual(0.6, price_a, places=4)
        self.assertAlmostEqual(8.0, price_b, places=4)


    def testGetPriceUnweightedTruthful(self):
        # act
        price_a = getPrice(self.advertiser_a, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, False, False)
        price_b = getPrice(self.advertiser_b, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, False, False)
        # assert
        self.assertAlmostEqual(20, price_a, places=4)
        self.assertAlmostEqual(10, price_b, places=4)


    def testGetPriceUnweightedNonTruthful(self):
        # act
        price_a = getPrice(self.advertiser_a, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, False, True)
        price_b = getPrice(self.advertiser_b, 300, 400, 10, 20, self.advertisers_a, self.advertisers_b, False, True)
        # assert
        self.assertAlmostEqual(10, price_a, places=4)
        self.assertAlmostEqual(20, price_b, places=4)


class AllocateRandomTest(unittest.TestCase):

    def setUp(self):
        self.a1_1 = Advertiser(4, 400, {'s1': 100, 's2': 100})
        self.a1_2 = Advertiser(2, 200, {'s1': 100, 's2': 100})
        self.b1_1 = Advertiser(3, 300, {'s1': 100, 's2': 100})
        self.b1_2 = Advertiser(1, 100, {'s1': 100, 's2': 100})
    

    def testWeighted(self):
        # arrange
        advertisers_a = [self.a1_1, self.a1_2]
        advertisers_b = [self.b1_1, self.b1_2]
        # act
        revenue, _ = allocateRandom(advertisers_a, advertisers_b, 2.5, 3.5, 400, 600, True, False)
        # assert
        self.assertAlmostEqual(500, revenue, places=4)
    

    def testUnweighted(self):
        # arrange
        advertisers_a = [self.a1_1, self.a1_2]
        advertisers_b = [self.b1_1, self.b1_2]
        # act
        revenue, _ = allocateRandom(advertisers_a, advertisers_b, 2.5, 3.5, 400, 600, False, False)
        # assert
        self.assertAlmostEqual(600, revenue, places=4)


    def testWeightedNonTruthful(self):
        # arrange
        advertisers_a = [self.a1_1, self.a1_2]
        advertisers_b = [self.b1_1, self.b1_2]
        # act
        revenue, _ = allocateRandom(advertisers_a, advertisers_b, 3.5, 2.5, 600, 400, True, True)
        # assert
        self.assertAlmostEqual(500, revenue, places=4)
    

    def testUnweightedNonTruthful(self):
        # arrange
        advertisers_a = [self.a1_1, self.a1_2]
        advertisers_b = [self.b1_1, self.b1_2]
        # act
        revenue, _ = allocateRandom(advertisers_a, advertisers_b, 3.5, 2.5, 600, 400, False, True)
        # assert
        self.assertAlmostEqual(600, revenue, places=4)


if __name__ == '__main__':
    unittest.main()