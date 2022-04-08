import * as React from 'react';
import TextField from '@mui/material/TextField';
import AdapterDate from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DatePicker from '@mui/lab/DatePicker';

export default function BasicDatePicker(props) {
  const [val, setVal] = React.useState(props.defaultValue);

  const handleChange = (date) => {
        setVal(date);
        props.handleChange(date);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDate}>
      <DatePicker
        label={props.label}
        value={val}
        defaultValue={props.defaultValue}
        onChange={handleChange}
        renderInput={(params) => <TextField {...params} />}
      />
    </LocalizationProvider>
  );
}
