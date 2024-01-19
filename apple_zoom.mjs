
import { Zoom, ZoomState } from '/Users/ferry.djaja/node_modules/zoomino/lib/zoom.js';
import PubNub from 'pubnub';

const pubnub = new PubNub({
  publishKey: "pub-c",
  subscribeKey: "sub-c",
  userId: "12",
});

const zoom = new Zoom();

// add listener
const listener = {
    status: (statusEvent) => {
        if (statusEvent.category === "PNConnectedCategory") {
            console.log("Connected");
        }
    },
    message: (messageEvent) => {
        showMessage(messageEvent.message.description);
    },
    presence: (presenceEvent) => {
        // handle presence
    }
};
pubnub.addListener(listener);

// subscribe to a channel
pubnub.subscribe({
    channels: ["hello_world"],
});


const showMessage = async (msgContent) => {
    console.log("message: " + msgContent);
    if(msgContent === 'mute') {
    	try {
          await zoom.mute();
        } catch {
          console.log('could not mute');
        }
    } else {
    	try {
          await zoom.unmute();
        } catch {
          console.log('could not unmute');
        }
    }


}

async function start () {

	
	//zoom.unmute();
	
	zoom.on('state-update', (state) => {
    	console.log('zoom state update %s', state);
	});

	zoom.start();
};

start();
