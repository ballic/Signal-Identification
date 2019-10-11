#!/usr/bin/env python3

import math, logging, threading, concurrent.futures

import numpy
import simplespectral
import os

from soapypower import threadpool

logger = logging.getLogger(__name__)

import time
from sklearn import datasets
from sklearn.cluster import SpectralClustering

import pickle

############################ start ############################
def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        files.sort(key = None)
        #print(root)
        #print(dirs)
        #files = files.replace('\n', '')
        print("[Main]: Path:" + str(file_dir) + ", Files Num:" + str(len(files)))
    return files

min_noise = 90000
max_signal = 70000
isNoise = 0 #0 noise   1 signal
############################ end ############################


class PSD:
    """Compute averaged power spectral density using Welch's method"""
    def __init__(self, bins, sample_rate, fft_window='hann', fft_overlap=0.5,
                 crop_factor=0, log_scale=True, remove_dc=False, detrend=None,
                 lnb_lo=0, max_threads=0, max_queue_size=0):
        self._bins = bins
        self._sample_rate = sample_rate
        self._fft_window = fft_window
        self._fft_overlap = fft_overlap
        self._fft_overlap_bins = math.floor(self._bins * self._fft_overlap)
        self._crop_factor = crop_factor
        self._log_scale = log_scale
        self._remove_dc = remove_dc
        self._detrend = detrend
        self._lnb_lo = lnb_lo
        self._executor = threadpool.ThreadPoolExecutor(
            max_workers=max_threads,
            max_queue_size=max_queue_size,
            thread_name_prefix='PSD_thread'
        )
        self._base_freq_array = numpy.fft.fftfreq(self._bins, 1 / self._sample_rate)
        self.samples = []#

    def set_center_freq(self, center_freq):
        """Set center frequency and clear averaged PSD data"""
        psd_state = {
            'repeats': 0,
            'freq_array': self._base_freq_array + self._lnb_lo + center_freq,
            'pwr_array': None,
            'update_lock': threading.Lock(),
            'futures': [],
        }
        return psd_state

    def result(self, psd_state):
        """Return freqs and averaged PSD for given center frequency"""
        freq_array = numpy.fft.fftshift(psd_state['freq_array'])
        pwr_array = numpy.fft.fftshift(psd_state['pwr_array'])

        if self._crop_factor:
            crop_bins_half = round((self._crop_factor * self._bins) / 2)
            freq_array = freq_array[crop_bins_half:-crop_bins_half]
            pwr_array = pwr_array[crop_bins_half:-crop_bins_half]

        if psd_state['repeats'] > 1:
            pwr_array = pwr_array / psd_state['repeats']

        if self._log_scale:
            pwr_array = 10 * numpy.log10(pwr_array)

        ############################ start ############################
        #print(self.samples)#
        #iq_data_file = open('/home/zjchen/data2/1', 'w')
        #numpy.set_printoptions(threshold = numpy.inf)
        #iq_data_file.write(str(self.samples))
        #iq_data_file.close()
        if max(pwr_array) > -114.97:
            print('[Samples]: pwr_array  max: %fdBm , It is signal (!_!).o0O' % max(pwr_array))#
        else:
            print('[Samples]: pwr_array  max: %fdBm , It is noise (@_@).o0O' % max(pwr_array))#
        ####### Save Path #######
        en_data_file = open('/home/zjchen/data2/trainss_data_en', 'a')
        en_data_file.write(str(max(pwr_array)) + " ")
        en_data_file.close()

        #print(pwr_array)#

        f = open('./config_count', 'r')
        count = f.read()
        count = count.replace('\n', '')
        f.close()
        '''
        if numpy.sum(pwr_array > -100) == 0:
            print("[Samples]: It is noise !!!")#
            #iq_data_file = open('/home/zjchen/data2/20190523/noise/' + str(freq_array[0]) + "_" + str(count), 'w')
            iq_data_file = open('/media/zjchen/5b8cbd15-7a4b-45cd-bfde-b139ad4b725b/zjchen/data2/20190523/noise/' + str(freq_array[0]) + "_" + str(count), 'w')
        else:
            print("[Samples]: It is signal !!!")#
            #iq_data_file = open('/home/zjchen/data2/20190523/signal/' + str(freq_array[0]) + "_" + str(count), 'w')
            iq_data_file = open('/media/zjchen/5b8cbd15-7a4b-45cd-bfde-b139ad4b725b/zjchen/data2/20190523/signal/' + str(freq_array[0]) + "_" + str(count), 'w')
        '''

        print("[Samples]: Get data !!!")#
        
        ####### Save Path #######
        iq_data_file = open('/media/zjchen/5b8cbd15-7a4b-45cd-bfde-b139ad4b725b/zjchen/data2/20190826-lab_signals_test/iq/' + str(freq_array[0]) + "_iq" + "_" + time.strftime("%m%d%H%M%S", time.localtime()) + "_" + str(count), 'w')
        #iq_data_file = open('/home/mm/data2/20190615/' + str(freq_array[0]) + "_iq" + "_" + time.strftime("%H%M%S", time.localtime()) + "_" + str(count), 'w')
        ####### Save Path #######
        power_data_file = open('/media/zjchen/5b8cbd15-7a4b-45cd-bfde-b139ad4b725b/zjchen/data2/20190826-lab_signals_test/pow/' + str(freq_array[0]) + "_pow" + "_" + time.strftime("%m%d%H%M%S", time.localtime()) + "_" + str(count), 'w')
        #power_data_file = open('/home/mm/data2/20190615/' + str(freq_array[0]) + "_pow" + "_" + time.strftime("%H%M%S", time.localtime()) + "_" + str(count), 'w')


        print("[Samples]: Saving file data: " + str(freq_array[0]) + ". Waiting...")
        numpy.set_printoptions(threshold = numpy.inf)
        iq_data_file.write(str(self.samples))
        iq_data_file.close()
        power_data_file.write(str(pwr_array))
        power_data_file.close()
        

        print("[Samples]: Done")
        print('[Samples]: Tw: %d' % ((min_noise - max_signal) / 2 + max_signal))
        print("--------------- end ---------------")
        #print(freq_array)#
        #time.sleep(1)
        ############################ end ############################

        return (freq_array, pwr_array)

    def wait_for_result(self, psd_state):
        """Wait for all PSD threads to finish and return result"""
        if len(psd_state['futures']) > 1:
            concurrent.futures.wait(psd_state['futures'])
        elif psd_state['futures']:
            psd_state['futures'][0].result()
        return self.result(psd_state)

    def result_async(self, psd_state):
        """Return freqs and averaged PSD for given center frequency (asynchronously in another thread)"""
        return self._executor.submit(self.wait_for_result, psd_state)

    def _release_future_memory(self, future):
        """Remove result from future to release memory"""
        future._result = None

    def update(self, psd_state, samples_array):
        """Compute PSD from samples and update average for given center frequency"""

        ############################ start ############################
        ### Get the same point
        print("--------------- start ---------------")
        point_map = {}
        xpos = []
        ypos = []
        zpos = []
        #print(samples_array)
        #print(len(samples_array))
        for item in samples_array:
            s = str(item)
            if s in point_map.keys():
                point_map[s] = point_map[s] + 1
            else:
                point_map[s] = 1

        array_component = [];    

        for key in point_map.keys():
            x_max = 1000
            y_max = 1000
            z_max = 100
            x_index = int(numpy.around(complex(key).real, 3) * 1000)
            y_index = int(numpy.around(complex(key).imag, 3) * 1000)
            #x_index = int(complex(key).real * 1000)
            #y_index = int(complex(key).imag * 1000)
            z_index = int(point_map[key] / 1)
            
            #print('%s的次数: %d, distance: %f' % (key, point_map[key], np.sqrt(pow(complex(key).real, 2) + pow(complex(key).imag, 2))))
            if x_index >= x_max or x_index < 0 or y_index >= y_max or y_index < 0 or z_index >= z_max:
                #print('[MC] Data out range ! Data locations : x:%f, y:%f, z:%f' % (x_index, y_index, z_ index))
                continue

            xpos.append(x_index)
            ypos.append(y_index)
            zpos.append(z_index)

            #zpos.append(0)
            #dz.append(point_map[key])
            #print('%f %f' % (complex(key).real, complex(key).imag))
            #print('distance is %f' % np.sqrt(pow(complex(key).real, 2) + pow(complex(key).imag, 2)))
            array_component.append(point_map[key])

        pickle.dump(xpos, open('/home/zjchen/data2/xpos', 'wb'))
        pickle.dump(ypos, open('/home/zjchen/data2/ypos', 'wb'))
        pickle.dump(zpos, open('/home/zjchen/data2/zpos', 'wb'))
        #print("@@@")
        #print(sorted(array_component))

        ####### Save Path #######
        ### 10 Cp & max Cp
        Cp = sorted(array_component)
        #print(Cp)
        Cp.remove(max(array_component))
        Cp_array = numpy.array(Cp)

        index = array_component.index(max(array_component))
        xpos_array3 = numpy.array(xpos)
        ypos_array3 = numpy.array(ypos)
        xpos_array3 = numpy.delete(xpos_array3, index)
        ypos_array3 = numpy.delete(ypos_array3, index)

        ###### X : ######
        ew_data_file = open('/home/zjchen/data2/trainss_data', 'w')
        if len(Cp_array) == 0:
            print('[Samples] NO Signal (@_@).o0O')
        threshold = int(max(Cp_array) / 5)
        #print(threshold)
        #print("########")
        index = numpy.argwhere(Cp_array > threshold)
        #print(index)
        xpos_array3 = numpy.delete(xpos_array3, index)
        ypos_array3 = numpy.delete(ypos_array3, index)
        dz_array3 = numpy.delete(Cp_array, index)
        #print(dz_array3)
        #ew_data_file.write(str(numpy.sum(dz_array3)))
        print('[Samples]: 5sum: %d' % numpy.sum(dz_array3))
        #ew_data_file.write(str(max(Cp)))
        #ew_data_file.write(str(max(array_component)))
        #ew_data_file.close()
        #print("@@@@@@@@")
        ###### Y : ######
        ### len Cp
        cp_data_file = open('/home/zjchen/data2/trainss_data2', 'w')
        cp_data_file.write(str(len(array_component)))
        cp_data_file.close()

        ### locations Cp
        '''
        max_ew_data_file = open('/home/zjchen/data2/trainss_data3', 'w')
        index = array_component.index(max(array_component))
        max_ew_data_file.write(str(index / len(array_component)))
        max_ew_data_file.close()
        '''
        #list_ew = numpy.array(sorted(array_component))
        #ten = list_ew[len(list_ew) - 2] / 10
        #print(ten)
        #print(list_ew)
        #print(numpy.argwhere(list_ew < ten))
        print('[Samples]: Len Cp: %d' % len(array_component))
        #index = len(numpy.argwhere(list_ew < ten))
        #print(index)

        ###### Z : ######
        test_data_file = open('/home/zjchen/data2/trainss_data3', 'w')
        #test_data_file.write(str(index / len(array_component)))
        #test_data_file.write(str(max(Cp)))
        #print('[Samples]: Max Cp: %d' % max(Cp))

        ### cluster
        xpos3 = xpos_array3.tolist()
        ypos3 = ypos_array3.tolist()
        dz3 = dz_array3.tolist()
        circles = numpy.array(list(zip(xpos3, ypos3)))

        #print(circles)
        sc = SpectralClustering(n_clusters=2, affinity="nearest_neighbors")

        sc_clusters2 = sc.fit_predict(circles)
        #print(sc_clusters2)
        print('[Samples]: Circle in number:%d' % len(numpy.argwhere(sc_clusters2 > 0)))
        test_data_file.write(str(len(numpy.argwhere(sc_clusters2 > 0))))
        test_data_file.close()



        ###### X : ######
        dz_sum = dz3 * sc_clusters2
        index = numpy.argwhere(dz_sum < 1)
        dz_sum = numpy.delete(dz_sum, index)
        print('[Samples]: Circle in sum:%d' % numpy.sum(dz_sum))
        ew_data_file.write(str(numpy.sum(dz_sum)))
        ew_data_file.close()


        print('[Samples]: Ew: %d' % max(array_component))
        ############################ end ############################


        ############################ start ############################
        ### reshow
        '''
        path_data = '/media/zjchen/5b8cbd15-7a4b-45cd-bfde-b139ad4b725b/zjchen/data2/20190722(lab)/iq/-110dbm/'
        files = file_name(path_data)
        files = sorted(files, key=len)
        #print(files)
        for i in range(0, len(files)):
            f = open(path_data + files[i], 'r')
            folder = f.read()
            f.close()

            print("[Main]: i:" + str(i + 1) + ", Finish File:" + str(files[i]))

            folder = folder.replace('\n', '')
            folder = re.sub(' +', ' ', folder)
            folder = folder.replace('[', '')
            folder = folder.replace(']', '')
            
            print(samples_array)

            
            dlist = folder.strip(' ').split(' ')  
            dint = list(map(complex, dlist))     
            darr =  np.array(dint)   
            
            
            print(len(folder))
            freq_array, pwr_array = simplespectral.welch(folder, self._sample_rate, nperseg=self._bins,
                                                     window=self._fft_window, noverlap=self._fft_overlap_bins,
                                                     detrend=self._detrend)
            print(pwr_array)
            exit()
        '''
        ############################ end ############################


        freq_array, pwr_array = simplespectral.welch(samples_array, self._sample_rate, nperseg=self._bins,
                                                     window=self._fft_window, noverlap=self._fft_overlap_bins,
                                                     detrend=self._detrend)
        ############################ start ############################
        #print("@@@@@@@@@@@@@@@@@@@@@@ self._buffer in psd() Start @@@@@@@@@@@@@@@@@@@@@@")#
        #print(pwr_array)#
        #print(freq_array)#
        #print(samples_array)#
        self.samples = samples_array
        #print(self.samples)#
        '''
        print(samples_array)#
        iq_data_file = open('/home/zjchen/data2/1', 'w')
        numpy.set_printoptions(threshold = numpy.inf)
        iq_data_file.write(str(samples_array))
        iq_data_file.close()
        '''
        #print("@@@@@@@@@@@@@@@@@@@@@@ self._buffer in psd() End   @@@@@@@@@@@@@@@@@@@@@@")#
        ############################ end ############################
        if self._remove_dc:
            pwr_array[0] = (pwr_array[1] + pwr_array[-1]) / 2

        with psd_state['update_lock']:
            psd_state['repeats'] += 1
            if psd_state['pwr_array'] is None:
                psd_state['pwr_array'] = pwr_array
            else:
                psd_state['pwr_array'] += pwr_array

    def update_async(self, psd_state, samples_array):
        """Compute PSD from samples and update average for given center frequency (asynchronously in another thread)"""
        future = self._executor.submit(self.update, psd_state, samples_array)
        future.add_done_callback(self._release_future_memory)
        psd_state['futures'].append(future)
        return future
