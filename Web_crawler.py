import re
import mechanize
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import sys
from datetime import datetime 
import sched

class getFares():	
	
	#self.browser = webdriver.Firefox()
	#self.browser.get('http://www.united.com/web/en-US/default.aspx?root=1')
	def __init__(self, src, dest, dptdt, retdt):
		self.src = src
		self.dest = dest
		self.dptdt = dptdt
		self.retdt = retdt
		self.p_arrdt = []
		self.p_flghtlist = []
		self.p_dpttime = []
		self.p_arrtime = []
		self.a_flghtlist = []
		self.a_awards = []
		self.p_fare = []
		self.d_res = {}	
	
	def fillDtls(self):

		#user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")

		#dcap = dict(DesiredCapabilities.PHANTOMJS)
		#dcap["phantomjs.page.settings.userAgent"] = user_agent
		
		browser = webdriver.Firefox()#PhantomJS(desired_capabilities=dcap)
		browser.get('http://www.united.com/web/en-US/default.aspx?root=1')
		#time.sleep(3)
		From = browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_Origin_txtOrigin")]')
		From.send_keys(self.src)
		From.send_keys(Keys.ARROW_DOWN)		
		
		To = browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_Destination_txtDestination")]')
		To.send_keys(self.dest)
		To.send_keys(Keys.ARROW_DOWN)

		departDt = browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_DepDateTime_Depdate_txtDptDate")]')
		departDt.send_keys(self.dptdt)
		
		returnDt = browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_RetDateTime_Retdate_txtRetDate")]')
		returnDt.send_keys(self.retdt)
		
		print "Search Criteria: Price"
		
		browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_SearchBy_rdosearchby1")]').click()
		print "criteria selected"
		
		browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_btnSearchFlight")]').click()	

		try:
			dtls = browser.find_elements_by_xpath('//tr[contains(@id, "trSegBlock")]')#/tr[1]/td[contains(@class, "tdSegmentDtl")]/div[1]/b')
			#p_flghtlist = []
			for i in dtls:
				flights = i.find_elements_by_xpath('.//td/table/tbody/tr/td[contains(@class, "tdSegmentDtl")]/div[1]')
				tmp_list = []
				for j in flights:
					tmp_list.append(j.find_element_by_tag_name("b").text)
				self.p_flghtlist.append(tmp_list)

			n = 1
			for i in dtls:
				self.p_dpttime.append(i.find_element_by_xpath('.//td/table/tbody/tr[1]/td[contains(@class, "tdDepart")]/div[2]/strong').text)
				try:
					self.p_arrtime.append(i.find_element_by_xpath('./td/table/tbody/tr[last()-1 ]/td[contains(@class, "tdArrive")]/div[2]/strong').text)
					self.p_arrdt.append(i.find_element_by_xpath('./td/table/tbody/tr[last()-1]/td[contains(@class, "tdArrive")]/div[3]/b').text)
				except NoSuchElementException:
					self.p_arrtime.append(i.find_element_by_xpath('./td/table/tbody/tr[last()]/td[contains(@class, "tdArrive")]/div[2]/strong').text)
					self.p_arrdt.append(i.find_element_by_xpath('./td/table/tbody/tr[last()]/td[contains(@class, "tdArrive")]/div[3]/b').text)

				self.p_fare.append(i.find_element_by_xpath('.//span[contains(@class, "fResultsPrice")]').text)
			#print self.p_dpttime
			#print self.p_arrtime
			#print self.p_arrdt
			#print self.p_fare

		
			print "Search Criteria: Award Points"
		
			browser.find_element_by_xpath('//input[contains(@id, "00_ContentInfo_Results_SearchBox_SearchBy_rdosearchby3")]').click()
			try:
			    element = WebDriverWait(browser, 10).until(
				EC.element_to_be_clickable((By.ID, "ctl00_ContentInfo_Results_SearchBox_btnSearch"))
			    )
			finally:
			    None #driver.quit()

			print "criteria selected"
			browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Results_SearchBox_btnSearch")]').click()	

			dtls = browser.find_elements_by_xpath('//table[contains(@class, "rewardResults")]/tbody[2]/tr')					

			for i in dtls:
				try:
					self.a_awards.append(i.find_element_by_xpath('.//td[2]/div[contains(@class, "divMileage")]').text)
				except NoSuchElementException:
					None
			
				flights = i.find_elements_by_xpath('.//td[contains(@class, "tdSegmentBlock")]/table/tbody/tr/td[contains(@class, "tdSegmentDtl")]/div[1]')
				#print n 
			
				tmp_list = []
				for j in flights:
					tmp_list.append(j.find_element_by_tag_name("b").text)
			
				self.a_flghtlist.append(tmp_list)
		
			n = 1
			for i in range(0,len(self.p_flghtlist)):
				for j in range(0,len(self.a_flghtlist)):
					if self.p_flghtlist[i] == self.a_flghtlist[j]:
						#print "success"
						self.d_res[n] = [datetime.strptime(self.p_arrdt[i],'%a., %b. %d, %Y').strftime('%m/%d/%Y'), self.p_flghtlist[i], self.p_dpttime[i], self.p_arrtime[i], self.p_fare[i], self.a_awards[j]]
						n += 1
				#else:
					#del self.p_flghtlist[i]
					#del self.p_dpttime[i]
					#del self.p_arrtime[i]
					#del self.p_fare[i]
					#i -= 1

		except NoSuchElementException:
			print "Wrong Parameter Values"	
		browser.close()
		self.writeCSV()
	
	def writeCSV(self):
		with open('results.csv','w') as csvfile:
			fieldnames = ['From','To','Depart Date','Arrive Date','Flight #','Time Depart','Time Arrive','Lowest Price','Award Points']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()

			for i in range(1,len(self.d_res.keys())):
				writer.writerow({'From':self.src, 'To':self.dest, 'Depart Date':self.dptdt, 'Arrive Date':self.d_res[i][0], 'Flight #':self.d_res[i][1], 'Time Depart':self.d_res[i][2], 'Time Arrive':self.d_res[i][3], 'Lowest Price':self.d_res[i][4], 'Award Points':self.d_res[i][5]})
		
	
myClassObject = getFares(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

s = sched.scheduler(time.time, time.sleep)
s.enter(int(sys.argv[5]), 1, myClassObject.fillDtls(), ())
s.run()
#myClassObject.fillDtls()
