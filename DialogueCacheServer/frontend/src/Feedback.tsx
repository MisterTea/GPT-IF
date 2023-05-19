import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';
import { observer } from 'mobx-react';
import * as React from 'react';
import DataStore from './datastore';

const FormDialog = observer(({ datastore }: { datastore: DataStore }) => {
    const feedbackValueRef: React.MutableRefObject<any> = React.useRef(''); //creating a refernce for TextField Component

    const handleCancel = () => {
        datastore.closeFeedback();
    };

    const handleFeedback = () => {
        datastore.handleFeedback(feedbackValueRef.current.value);
    };

    return (
        <div>
            <Dialog open={datastore.feedbackModal} onClose={handleCancel}>
                <DialogTitle>Give Feedback</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        How can we make GptIf better?
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="feedback"
                        label="Feedback"
                        fullWidth
                        multiline
                        variant="standard"
                        inputRef={feedbackValueRef}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleFeedback} variant="contained">Send</Button>
                    <Button onClick={handleCancel} variant="text">Cancel</Button>
                </DialogActions>
            </Dialog>
        </div>
    );
});

export default FormDialog;
