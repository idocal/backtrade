import * as React from 'react';
import TextField from '@mui/material/TextField';
import AdapterDate from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DatePicker from '@mui/lab/DatePicker';
import format from 'date-fns/format';

export default function BasicDatePicker(props) {
  const [val, setVal] = React.useState(null);

  const handleChange = (date) => {
        let formatted = format(date, "yyyy-MM-dd");
        setVal(date);
        props.handleChange(formatted);
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
