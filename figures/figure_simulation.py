# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the generation of the figures of simulation experiments

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
import math

def draw_abort_rate(filename, xs, ys, a1_max, a2_max, x_title, x_labels=[]):
	plt.clf()

	font = {'size':40}
	mpl.rc('font', **font)

	n = len(xs)
	x = np.arange(n) + 1

	zkSync = np.array(ys[0]) * 100
	CAT = np.array(ys[1]) * 100
	Diff = np.array(ys[2]) * 100

	fig = plt.figure()
	# set the figure size ratio
	fig.set_size_inches(10, 7)

	# do not show the top-right line
	ax1 = fig.add_subplot(111)
	ax1.set_ylim([0, a1_max])
	ax1.yaxis.set_major_locator(ticker.MultipleLocator(20))
	# Set the title and the labels of x-axis and y-axis
	xText = ax1.set_xlabel(x_title, fontsize=40)
	y1Text = ax1.set_ylabel('Abort Rate (%)', fontsize=40)
	# draw bar chart
	plt.bar(x - 0.2, zkSync, width=0.4, label=r'$zkSync$', color='#ffffff', edgecolor='#1E90FF', lw=2)
	plt.bar(x + 0.2, CAT,    width=0.4, label=r'$zkCAT$', color='#ffffff', edgecolor='#83AF9B', lw=2, hatch='//')
	leg1 = ax1.legend(prop={'size': 30}, frameon = False,
		columnspacing=0.6,
		bbox_to_anchor=(0.72, 1.15), borderaxespad=0, ncol=2)
	for a,b in zip(x, zkSync):
		plt.text(a-0.2, b, '%.1f' % b, ha='center', va= 'bottom', fontsize=20)
	for a,b in zip(x, CAT):
		plt.text(a+0.2, b, '%.1f' % b, ha='center', va= 'bottom', fontsize=20)

	ax2 = ax1.twinx()
	# find the max of ys[0]/ys[1], set the ax2_y min as the max value
	y2Text = ax2.set_ylabel('Difference (%)', fontsize=40)
	# draw line chart
	plt.plot(x, Diff, label=r'$Diff$', linewidth=2, marker='x', markersize=20, color='#FE4365')
	# set the yticks
	ax2.set_ylim([0, a2_max])
	ax2.yaxis.set_major_locator(ticker.MultipleLocator(10))
	leg2 = ax2.legend(prop={'size': 30}, frameon = False, bbox_to_anchor=(1.0, 1.15), borderaxespad=0, ncol=2)
	for a,b in zip(x, Diff):
		plt.text(a, b+1, '%.1f' % b, ha='center', va= 'bottom', fontsize=20)

	# set the x label
	if x_labels:
		group_labels = x_labels
	else:
		# label is 2^x
		group_labels = []
		for temp_x in xs:
			temp_x = np.log2(temp_x)
			group_labels.append(r'$2^{%d}$' % temp_x)

	plt.xticks(x, group_labels, rotation=0)

	# plt.show()
	path = 'simulation/%s.pdf' % filename

	plt.savefig(path,
		bbox_extra_artists=(leg1, leg2, xText, y1Text, y2Text),
		bbox_inches='tight')

def draw_throughput_latency(filename, xs, ys, a1_max, a2_max, x_title, x_labels=[]):
	plt.clf()

	font = {'size':40}
	mpl.rc('font', **font)

	n = len(xs)
	x = np.arange(n) + 1

	zkSync_tps = np.array(ys[0])
	zkCAT_tps = np.array(ys[1])
	zkSync_lat = np.array(ys[2])
	zkCAT_lat = np.array(ys[3])

	fig = plt.figure()
	# set the figure size ratio
	fig.set_size_inches(13, 7)

	# do not show the top-right line
	ax1 = fig.add_subplot(111)
	ax1.set_ylim([0, a1_max])
	ax1.yaxis.set_major_locator(ticker.MultipleLocator(200))
	# Set the title and the labels of x-axis and y-axis
	xText = ax1.set_xlabel(x_title, fontsize=40)
	y1Text = ax1.set_ylabel('Throughput (tps)', fontsize=40)
	# draw bar chart
	plt.bar(x - 0.2, zkSync_tps, width=0.4, label=r'$zkSync-throughput$', color='#ffffff', edgecolor='#1E90FF', lw=2)
	plt.bar(x + 0.2, zkCAT_tps,  width=0.4, label=r'$zkCAT-throughput$', color='#ffffff', edgecolor='#83AF9B', lw=2, hatch='//')
	leg1 = ax1.legend(prop={'size': 25}, frameon = False, columnspacing=1.2,
		bbox_to_anchor=(0.5, 1.25), borderaxespad=0)

	for a,b in zip(x, zkSync_tps):
		plt.text(a-0.2, b, '%.1f' % b, ha='center', va='bottom', fontsize=16)
	for a,b in zip(x, zkCAT_tps):
		plt.text(a+0.2, b, '%.1f' % b, ha='center', va='bottom', fontsize=16)

	ax2 = ax1.twinx()
	# find the max of ys[0]/ys[1], set the ax2_y min as the max value
	y2Text = ax2.set_ylabel('Latency (s)', fontsize=40)
	# draw line chart
	plt.plot(x, zkSync_lat, label=r'$zkSync-latency$', linewidth=2, marker='^', markersize=16, color='#FFA500')
	plt.plot(x, zkCAT_lat, label=r'$zkCAT-latency$', linewidth=2, marker='o', markersize=16, color='#8A2BE2')
	# set the yticks
	ax2.set_ylim([0, a2_max])
	ax2.yaxis.set_major_locator(ticker.MultipleLocator(300))
	leg2 = ax2.legend(prop={'size': 25}, frameon = False, columnspacing=1.2,
					  bbox_to_anchor=(1.0, 1.25), borderaxespad=0)
	for a,b in zip(x, zkSync_lat):
		plt.text(a, b+30, '%.1f' % b, ha='center', va= 'bottom', fontsize=20)
	for a,b in zip(x, zkCAT_lat):
		plt.text(a, b+30, '%.1f' % b, ha='center', va= 'bottom', fontsize=20)

	# set the x label
	if x_labels:
		group_labels = x_labels
	else:
		# label is 2^x
		group_labels = []
		for temp_x in xs:
			temp_x = np.log2(temp_x)
			group_labels.append(r'$2^{%d}$' % temp_x)

	plt.xticks(x, group_labels, rotation=0)

	# plt.show()
	path = 'simulation/%s.pdf' % filename

	plt.savefig(path,
				bbox_extra_artists=(leg1, leg2, xText, y1Text, y2Text),
				bbox_inches='tight' )

if __name__ == '__main__':
	# abort rate - vary m
	xs1 = [32, 64, 128, 256, 512, 1024]
	ys1 = [[0.811, 0.82, 0.82, 0.823, 0.824, 0.821],
		  [0.729, 0.726, 0.696, 0.657, 0.605, 0.566],
		  [0.082, 0.094, 0.124, 0.166, 0.219, 0.255]]
	draw_abort_rate('abort_rate_vary_m', xs1, ys1, 100, 60, 'm')
	# vary failure rate
	xs2 = [0.03, 0.05, 0.08, 0.11, 0.15, 0.17]
	ys2 = [[0.395, 0.561, 0.716, 0.823, 0.887, 0.934],
		  [0.316, 0.451, 0.581, 0.657, 0.707, 0.743],
		  [0.079, 0.11, 0.135, 0.166, 0.18, 0.191]]
	draw_abort_rate('abort_rate_vary_failure_rate', xs2, ys2, 100, 40, r'$\rho$',
		['3%','5%','8%','11%','15%','17%'])
	# vary zipfian
	xs3 = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
	ys3 = [[0.806, 0.819, 0.829, 0.831, 0.824, 0.816],
		  [0.466, 0.502, 0.527, 0.555, 0.618, 0.722],
		  [0.34, 0.317, 0.302, 0.276, 0.206, 0.094]]
	draw_abort_rate('abort_rate_vary_zipfian', xs3, ys3, 100, 47, r'Zipfian coefficient $\theta$',
		['0', '0.4','0.8','1.2','1.6','2.0'])

	# abort rate - vary m
	xs4 = [32, 64, 128, 256, 512, 1024]
	ys4 = [[582.31, 584.42, 587.2, 582.77, 582.75, 583.12],
		   [605.31, 613.06, 618.89, 622.89, 624.12, 626.73],
		   [1326.11, 1325.44, 1323.59, 1325.68, 1324.78, 1325],
		   [1201.16, 1182.39, 1160.97, 1140.74, 1118.26, 1095.23]]
	draw_throughput_latency('tps_lat_vary_m_0_failure', xs4, ys4, 950, 1450, 'm')
	# vary failure rate
	xs5 = [0, 0.03, 0.06, 0.09, 0.12, 0.15]
	ys5 = [[582.77, 387.2, 267.74, 195.13, 151.71, 124.49],
		   [622.89, 430.91, 355.19, 276.1, 228.78, 200.65],
		   [1325.68, 1306.72, 1290.61, 1278.39,1273.13, 1262.82],
		   [1140.74, 1120.3, 1105.98, 1099.05, 1087.9, 1080.57]]
	draw_throughput_latency('tps_lat_vary_failure_rate', xs5, ys5, 950, 1450, r'$\rho$',
		['0%','3%','6%','9%','12%','15%'])
	# vary zipfian
	xs6 = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
	ys6 = [[203.21, 199.28, 199.59, 203.11, 205.19, 212.41],
		   [359.39, 354.08, 357, 367.84, 340.72, 300.13],
		   [1283.32, 1282.35, 1285.41, 1286.47, 1284.21, 1284.66],
		   [1077.08, 1076.99, 1080.47, 1089.47, 1105.43, 1116.9]]
	draw_throughput_latency('tps_lat_vary_zipfian', xs6, ys6, 800, 1450,
							r'Zipfian coefficient $\theta$', ['0', '0.4','0.8','1.2','1.6','2.0'])

	print("Done!")