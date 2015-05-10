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
from sys import argv, exit
from datetime import datetime 
import sched

class getFares(): #Class for crawling the website	
	
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
		self.browser = webdriver.Firefox()
	
	def fillDtls(self): #Function for filling in details

		#user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")

		#dcap = dict(DesiredCapabilities.PHANTOMJS)
		#dcap["phantomjs.page.settings.userAgent"] = user_agent
		
		#self.browser = webdriver.Firefox()#PhantomJS(desired_capabilities=dcap)
		self.browser.get('http://www.united.com/web/en-US/default.aspx?root=1') #Get response from the website

		#Enter the source value
		From = self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_Origin_txtOrigin")]')
		From.send_keys(self.src)
		From.send_keys(Keys.ARROW_DOWN)		
		
		#Enter the destination value
		To = self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_Destination_txtDestination")]')
		To.send_keys(self.dest)
		To.send_keys(Keys.ARROW_DOWN)

		#Enter the Departure Date value
		departDt = self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_DepDateTime_Depdate_txtDptDate")]')
		departDt.send_keys(self.dptdt)
		
		#Enter the Return Date value
		returnDt = self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_RetDateTime_Retdate_txtRetDate")]')
		returnDt.send_keys(self.retdt)
		#self.srchPrice()
		
	def srchPrice(self): #Function for Searching by Price
		print "Search Criteria: Price"
		
		#Select the radio button and click submit
		self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_SearchBy_rdosearchby1")]').click()
		print "criteria selected"
		
		self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Booking1_btnSearchFlight")]').click()	

		try:
			#Get the flight details from the table and traverse each of the option available
			#Append the flight details in a list p_flghtlist	
			
			dtls = self.browser.find_elements_by_xpath('//tr[contains(@id, "trSegBlock")]')#/tr[1]/td[contains(@class, "tdSegmentDtl")]/div[1]/b')
			#p_flghtlist = []
			for i in dtls:
				flights = i.find_elements_by_xpath('.//td/table/tbody/tr/td[contains(@class, "tdSegmentDtl")]/div[1]')
				tmp_list = []
				for j in flights:
					tmp_list.append(j.find_element_by_tag_name("b").text)
				self.p_flghtlist.append(tmp_list)
			
			# Get the departure time and arrival time of the flights and store them in seperate lists 	
			
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
			#self.srchAwards()
		except NoSuchElementException:
			print "Wrong Parameter Values"	

	def srchAwards(self): #Function for searching by Award miles
		try:	
			print "Search Criteria: Award Points"
		
			self.browser.find_element_by_xpath('//input[contains(@id, "00_ContentInfo_Results_SearchBox_SearchBy_rdosearchby3")]').click()
			
			print "criteria selected"
			self.browser.find_element_by_xpath('//input[contains(@id, "ctl00_ContentInfo_Results_SearchBox_btnSearch")]').click()	

			dtls = self.browser.find_elements_by_xpath('//table[contains(@class, "rewardResults")]/tbody[2]/tr')					

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
		
			# Compare the details obtained by both search criteria and filter out the common flight options
			# Store the required details in a dictionary
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

		#self.browser.close()
		#self.writeCSV()
	
	def writeCSV(self): # Function for writing data into results.csv file from result dictionary
		with open('results.csv','w') as csvfile:
			fieldnames = ['From','To','Depart Date','Arrive Date','Flight #','Time Depart','Time Arrive','Lowest Price','Award Points']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()

			for i in range(1,len(self.d_res.keys())):
				writer.writerow({'From':self.src, 'To':self.dest, 'Depart Date':self.dptdt, 'Arrive Date':self.d_res[i][0], 'Flight #':self.d_res[i][1], 'Time Depart':self.d_res[i][2], 'Time Arrive':self.d_res[i][3], 'Lowest Price':self.d_res[i][4], 'Award Points':self.d_res[i][5]})
			
			print "results.csv updated"
		
def Start():
	myClassObject = getFares(argv[1],argv[2],argv[3],argv[4])	
	myClassObject.fillDtls()
	myClassObject.srchPrice()
	myClassObject.srchAwards()
	myClassObject.browser.close()
	myClassObject.writeCSV()

def delay(interval):
	print time.time()
	s.enter(1, 1, Start, ())
	time.sleep(interval)
	return 1

if __name__ == "__main__":
	if len(argv) != 6:
    		print 'usage: %s <Source> <Destination> <Dept Date> <Return Date> <Interval>' %argv[0]
    		exit(1)

  	#myClassObject = getFares(argv[1],argv[2],argv[3],argv[4])
	s = sched.scheduler(time.time, time.sleep)
	#s.enter(1, 1, Start, ())
	#s.run()

	while delay(int(argv[5])*60):
		#s.enter(1, 1, Start, ())
		s.run()
	
#myClassObject.fillDtls()
