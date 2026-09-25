import { useState } from 'react';
import {
    Alert,
    Button,
    CircularProgress,
    Stack,
    Typography,
} from '@mui/material';
import styles from '../components/styles/QRGenerator.module.less';
import { checkUpdates, startUpdate, type UpdateStatus } from '../api/settings';

export default function Settings() {
    const [updateStatus, setUpdateStatus] = useState<UpdateStatus | null>(null);
    const [isChecking, setIsChecking] = useState(false);
    const [isStarting, setIsStarting] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const checkForUpdates = async () => {
        setIsChecking(true);
        setMessage(null);
        setError(null);

        try {
            setUpdateStatus(await checkUpdates());
        } catch (requestError) {
            setError(requestError instanceof Error ? requestError.message : 'Unable to check for updates.');
        } finally {
            setIsChecking(false);
        }
    };

    const startUpdateProcess = async () => {
        setIsStarting(true);
        setMessage(null);
        setError(null);

        try {
            const response = await startUpdate();
            setMessage(response.status === 'update_started'
                ? 'Update started. The application will restart shortly.'
                : response.status);
        } catch (requestError) {
            setError(requestError instanceof Error ? requestError.message : 'Unable to start update.');
        } finally {
            setIsStarting(false);
        }
    };

    return (
        <main>
            <section className={styles.card}>
                <Stack spacing={2}>
                    <Typography variant="h5">Updates</Typography>
                    <Button
                        onClick={checkForUpdates}
                        disabled={isChecking || isStarting}
                        variant="outlined"
                    >
                        {isChecking ? <CircularProgress size={20} /> : 'Check for Updates'}
                    </Button>

                    {updateStatus && (
                        <Typography>
                            Current: {updateStatus.current_version || 'untagged'}{' '}
                            | Latest: {updateStatus.latest_version}
                        </Typography>
                    )}

                    {updateStatus?.update_available && (
                        <>
                            <Button
                                onClick={startUpdateProcess}
                                disabled={isStarting || isChecking}
                                variant="contained"
                                color="warning"
                            >
                                {isStarting ? <CircularProgress size={20} /> : `Update to ${updateStatus.latest_version}`}
                            </Button>
                        </>
                    )}

                    {message && <Alert severity="success">{message}</Alert>}
                    {error && <Alert severity="error">{error}</Alert>}
                </Stack>
            </section>
        </main>
    )
}