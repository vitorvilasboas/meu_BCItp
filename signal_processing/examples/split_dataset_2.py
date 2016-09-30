import sys

sys.path.insert(1, '../')

from approach import Approach
import numpy as np
import math

from random import randint

from DataManipulation import saveMatrixAsTxt, extractEpochs, loadDataAsMatrix, \
    readEvents

DATA_FOLDER_PATH = "/home/rafael/codes/bci_training_platform/data/session/A1_comp/"
EVENTS_FOLDER_PATH = "/home/rafael/codes/bci_training_platform/data/session/A1_comp/"

DATA_PATH = DATA_FOLDER_PATH + "data_cal.npy"

# EVENTS INFO PATH
EVENTS_PATH = EVENTS_FOLDER_PATH + "events_cal.npy"

SAMPLING_FREQ = 250.0

# EPOCH EXTRACTION CONFIG:
EVENT_IDS = [769, 770, 771, 772]

T_MIN, T_MAX = 0.5, 2.5  # time before event, time after event

smin = int(math.floor(T_MIN * SAMPLING_FREQ))
smax = int(math.floor(T_MAX * SAMPLING_FREQ))

data = loadDataAsMatrix(DATA_PATH).T
events = readEvents(EVENTS_PATH)

data = data[0:22]

epochs_good, labels_good = extractEpochs(data,
                                         events,
                                         smin,
                                         smax,
                                         EVENT_IDS)

idx_left = np.where(labels_good == EVENT_IDS[0])[0]
idx_right = np.where(labels_good == EVENT_IDS[1])[0]
idx_foot = np.where(labels_good == EVENT_IDS[2])[0]
idx_tongue = np.where(labels_good == EVENT_IDS[3])[0]

# EPOCH EXTRACTION CONFIG:
EVENT_IDS = [0]

T_MIN, T_MAX = 0, 1.5  # time before event, time after event

smin = int(math.floor(T_MIN * SAMPLING_FREQ))
smax = int(math.floor(T_MAX * SAMPLING_FREQ))

epochs_bad, labels_bad = extractEpochs(data,
                                       events,
                                       smin,
                                       smax,
                                       EVENT_IDS)

idx_none = np.where(labels_bad == EVENT_IDS[0])[0]


# Generating new dataset

new_data = np.zeros([1, epochs_good.shape[1]])
new_events = np.zeros([1, 2])

idx1 = idx_right
idx2 = idx_tongue
idx3 = idx_none

label1 = labels_good[idx1[0]]
label2 = labels_good[idx2[0]]
label3 = labels_bad[idx3[0]]

for j in range(4):
    for i in range(8):
        k = randint(0, len(idx3))
        new_events = np.vstack([new_events, [new_data.shape[0], label3]])
        new_data = np.vstack([new_data, epochs_bad[idx3[i]].T])

    for i in range(5):
        k = randint(0, len(idx1))
        new_events = np.vstack([new_events, [new_data.shape[0], label1]])
        new_data = np.vstack([new_data, epochs_good[idx1[i]].T])

# for i in range(10):
#     k = randint(0, len(idx1))
#     new_events = np.vstack([new_events, [new_data.shape[0], label1]])
#     new_data = np.vstack([new_data, epochs_good[idx1[i]].T])

# for i in range(40):
#     k = randint(0, len(idx2))
#     new_events = np.vstack([new_events, [new_data.shape[0], label2]])
#     new_data = np.vstack([new_data, epochs_good[idx2[i]].T])

new_data = np.delete(new_data, 0, axis=0)
new_events = np.delete(new_events, 0, axis=0)

SAVE_PATH = '/media/rafael/a8062025-4bf2-4357-aa0a-553348489b90/home/rafael/eeg_data/compIV/split_datasets\
/split1.npy'

NEW_EVENTS_PATH = '/media/rafael/a8062025-4bf2-4357-aa0a-553348489b90/home/rafael/eeg_data/compIV/split_datasets\
/split1_events.npy'

saveMatrixAsTxt(new_data, SAVE_PATH)
saveMatrixAsTxt(new_events, NEW_EVENTS_PATH)
