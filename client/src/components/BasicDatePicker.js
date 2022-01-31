import * as React from 'react';
import TextField from '@mui/material/TextField';
import AdapterDate from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DatePicker from '@mui/lab/DatePicker';
import { isValid, format } from 'date-fns';

export default function BasicDatePicker(props) {
  const [val, setVal] = React.useState(null);

  const handleChange = (date) => {
        setVal(date);
        if (isValid(date)) {
            let formatted = format(date, "yyyy-MM-dd");
            props.handleChange(formatted);
        }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDate}>
      <DatePicker
        label={props.label}
        value={val}
        onChange={handleChange}
        renderInput={(params) => <TextField {...params} />}
      />
    </LocalizationProvider>
  );
}
