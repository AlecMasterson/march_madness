import React from 'react';
import {Card, CardContent, Container, Grid, Tab, Tabs} from '@mui/material';
import {createTheme, Theme, ThemeProvider} from '@mui/material/styles';
import darkScrollbar from '@mui/material/darkScrollbar';
import {SnackbarProvider} from 'notistack';
import './app.css';

const DarkTheme: Theme = createTheme({
    components: {
        MuiCssBaseline: {
            styleOverrides: {body: darkScrollbar()}
        }
    },
    palette: {
        background: {default: '#201D39', paper: '#4E4868'},
        mode: 'dark',
        primary: {main: '#00C899'},
        secondary: {main: '#F4ECFF'}
    }
});

export default function App (): React.ReactElement {
    const [tab, setTab] = React.useState<number>(0);

    function onTabChange(_: React.SyntheticEvent, newTab: number): void {
        setTab(newTab);
    }

    return (
        <ThemeProvider theme={DarkTheme}>
            <SnackbarProvider>
                <Container>
                    <Grid item>
                        <Tabs className='main-tabs' centered={true} onChange={onTabChange} value={tab}>
                            <Tab label='Market View' />
                            <Tab label='Positions' />
                            <Tab label='Model Analysis' />
                            <Tab label='Admin Portal' />
                        </Tabs>
                    </Grid>

                    <Card variant='outlined' style={{maxWidth: '100px'}}>
                        <CardContent>
                            <span style={{width: '100%'}}>ALA</span>
                            <span>AMCC</span>
                        </CardContent>
                    </Card>


                    <div className="mW mW_1">
                        <div className="matchup m_1" data-index="0" data-id="63">
                            <a target="_blank">
                                <span className="score away">6</span>
                                <span className="dateStart">3:15 PM</span>
                                <span className="score home">9</span>
                                <span className="clock">
                                    <span>15:38</span><span>1st</span>
                                </span>
                            </a>
                            <div className="slots">
                                <div className="slot s_1">
                                    <span className="actual selectedToAdvance">
                                        <img className="logo" src="https://secure.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/333.png&amp;w=36&amp;h=36&amp;scale=crop"/>
                                        <span className="seed">1</span>
                                        <span className="abbrev" title="Alabama">ALA</span>
                                        <span className="name">Alabama</span>
                                    </span>
                                </div>
                                <div className="slot s_2">
                                    <span className="actual">
                                        <img className="logo" src="https://secure.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/357.png&amp;w=36&amp;h=36&amp;scale=crop"/>
                                        <span className="seed">16</span>
                                        <span className="abbrev" title="Texas A&amp;M-CC">AMCC</span>
                                        <span className="name">Texas A&amp;M-CC</span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div className="matchup m_2" data-index="1" data-id="64">
                            <a target="_blank" >
                                <span className="score away">65</span>
                                <span className="dateStart"></span>
                                <span className="score home win">67</span>
                                <span className="clock">Final</span>
                            </a>
                            <div className="slots">
                                <div className="slot s_1" data-slotindex="2" data-teamid="3">
                                    <span className="actual selectedToAdvance winner" data-sportsid="120" data-id="3">
                                        <img className="logo" src="https://secure.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/120.png&amp;w=36&amp;h=36&amp;scale=crop"/>
                                        <span className="seed">8</span>
                                        <span className="abbrev" title="Maryland">MD</span>
                                        <span className="name">Maryland</span>
                                    </span>
                                </div>
                                <div className="slot s_2" data-slotindex="3" data-teamid="4">
                                    <span className="actual loser" data-sportsid="277" data-id="4">
                                        <img className="logo" src="https://secure.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/277.png&amp;w=36&amp;h=36&amp;scale=crop"/>
                                        <span className="seed">9</span>
                                        <span className="abbrev" title="West Virginia">WVU</span>
                                        <span className="name">West Virginia</span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                </Container>
            </SnackbarProvider>
        </ThemeProvider>
    );
}
