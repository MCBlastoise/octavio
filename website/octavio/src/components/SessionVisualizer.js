import { useEffect, useRef, useState } from "react";
import { Player, PianoRollSVGVisualizer, midiToSequenceProto } from '@magenta/music';

import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import PauseRounded from '@mui/icons-material/PauseRounded';
import PlayArrowRounded from '@mui/icons-material/PlayArrowRounded';
// import PlayerCanvas from '@/components/PlayerCanvas';
import * as Tone from 'tone';
// import PlaybackSlider from "@/components/PlaybackSlider";

const Widget = styled('div')(({ theme }) => ({
  padding: 16,
  borderRadius: 16,
  width: 343,
  maxWidth: '100%',
  margin: 'auto',
  position: 'relative',
  zIndex: 1,
  backgroundColor: 'rgba(128,128,128,0.05)',
  backdropFilter: 'blur(40px)',
  ...theme.applyStyles('dark', {
    backgroundColor: 'rgba(0,0,0,0.6)',
  }),
}));

const TinyText = styled(Typography)({
  fontSize: '0.75rem',
  opacity: 0.38,
  fontWeight: 500,
  letterSpacing: 0.2,
});

export default function SessionVisualizer({ session_id, instrument_id }) {

    const [ midiSequence, setMidiSequence ] = useState(null);
    const svgRef = useRef(null);
    const [player, setPlayer] = useState(null);
    const [visualizer, setVisualizer] = useState(null);
    const animationRef = useRef(null);
    const scrollRef = useRef(null);

    useEffect(() => {
        fetch(`http://octavio-server.mit.edu:5001/api/midi?session_id=${session_id}&instrument_id=${instrument_id}`)
            .then(res => res.arrayBuffer())
            .then(arrayBuffer => setMidiSequence(midiToSequenceProto(arrayBuffer)))
    }, []);

    useEffect(() => {
        if (!midiSequence || !svgRef.current) return;

        // Create visualizer
        const vis = new PianoRollSVGVisualizer(
            midiSequence,
            svgRef.current,
            {
                noteHeight: 6,
                pixelsPerTimeStep: 60,
            });
        setVisualizer(vis);

        // Create player with run callback to update visualizer
        const newPlayer = new Player(false, {
            run: (note) => {
                vis.redraw(note);
                // setPosition(note.startTime);
                const scrollEl = scrollRef.current;
                const scrollPos = note.startTime * 60; // same as pixelsPerTimeStep
                scrollEl.scrollLeft = scrollPos - 100; // keep some margin
            },
            stop: () => {
                console.log('Playback finished');
                setPlayingState('finished');
            },
        });
        setPlayer(newPlayer);
    }, [midiSequence]);

    useEffect(() => {
        if (!player) return;

        const tick = () => {
          if (!isSeeking && player.isPlaying()) {
            const pos = Tone.Transport.seconds
            setPosition(pos);
            console.log("pos", pos);
          }
          animationRef.current = requestAnimationFrame(tick);
        };

        animationRef.current = requestAnimationFrame(tick);

        return () => {
          if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
          }
        };
    }, [player]);

    const handlePlay = () => {
        if (player && midiSequence) {
            // if (playingState === 'finished') {
            //     setPosition(0);
            // }
            // else {
            //     player.start(midiSequence);
            // }
            player.start(midiSequence);
        }
    };

    const handlePause = () => {
        if (player && midiSequence) {
            player.pause(midiSequence);
        }
    };

    const handleResume = () => {
        if (player && midiSequence) {
            player.resume(midiSequence);
        }
    };

    const handleSeek = (_, value) => {
        // setPlaybackTime(value);
        if (player && midiSequence && playingState != 'stopped' && playingState != 'finished') {
          setPosition(value);
          player.seekTo(value);
          visualizer.redraw(null);
        }
      };

    const duration = !midiSequence ? 0 : midiSequence.totalTime;

    // console.log(!midiSequence ? 'Nope' : midiSequence.totalTime)





    const [isSeeking, setIsSeeking] = useState(false);
    // const duration = 200; // seconds
    const [position, setPosition] = React.useState(0);
    console.log("position", position);
    // const [paused, setPaused] = React.useState(true);
    const [playingState, setPlayingState] = React.useState('stopped');
    function formatDuration(value) {
        const minute = Math.floor(value / 60);
        const secondLeft = Math.floor(value - minute * 60);
        // const secondLeft = value - minute * 60;
        return `${minute}:${secondLeft < 10 ? `0${secondLeft}` : secondLeft}`;
    }

    const sliderSx = {
        color: 'rgba(0,0,0,0.87)',
        height: 4,
      };

    // const sliderRef = useRef(null);

    // useEffect(() => {
    //     if (sliderRef.current) {
    //       // Manually set the slider's input value
    //       const input = sliderRef.current.querySelector('input[type="range"]');
    //       if (input) {
    //         input.value = position;
    //         input.dispatchEvent(new Event('input', { bubbles: true }));
    //       }
    //     }
    //   }, [position]);


  return (
    <Box sx={{ width: '100%', overflow: 'hidden', position: 'relative', p: 3 }}>
      <Widget>
        <Box ref={scrollRef} sx={{ overflowX: 'auto', overflowY: 'hidden', scrollbarWidth: 0 }}>
            <svg ref={svgRef} width={800} height={200} />
        </Box>

        {/* <PlaybackSlider duration={duration} position={position}></PlaybackSlider> */}

        <Slider
          key={Math.floor(position * 100)}
          aria-label="time-indicator"
          size="small"
          value={position}
          min={0}
          max={duration}
          step={0.01}
          onChange={(_, value) => {
            setIsSeeking(true);
            // setPosition(value);
          }}
          onChangeCommitted={(_, value) => {
            handleSeek(undefined, value)
            setIsSeeking(false);
            // player.seekToPosition(value);
          }}
          sx={sliderSx}
        />
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mt: -2,
          }}
        >
          <TinyText>{formatDuration(position)}</TinyText>
          <TinyText>{formatDuration(duration)}</TinyText>
        </Box>
        <Box
          sx={(theme) => ({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mt: -1,
            '& svg': {
              color: '#000',
              ...theme.applyStyles('dark', {
                color: '#fff',
              }),
            },
          })}
        >
          <IconButton
            aria-label={playingState == 'playing' ? 'pause' : 'play'}
            onClick={() => {
                if (playingState === 'stopped') {
                    handlePlay();
                    setPlayingState('playing');
                }
                else if (playingState === 'paused') {
                    handleResume();
                    setPlayingState('playing');
                }
                else if (playingState === 'playing') {
                    handlePause();
                    setPlayingState('paused');
                }
                else if (playingState === 'finished') {
                    handlePlay();
                    setPlayingState('playing');
                }
            }}
          >
            {playingState === 'playing' ? (
              <PauseRounded sx={{ fontSize: '3rem' }} />
            ) : (
              <PlayArrowRounded sx={{ fontSize: '3rem' }} />
            )}
          </IconButton>
        </Box>
      </Widget>
    </Box>
  );
}
