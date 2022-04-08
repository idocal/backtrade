import * as React from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

export default function BasicSelect(props) {
  const [val, setVal] = React.useState('');

  const handleChange = (event) => {
    setVal(event.target.value);
    props.handleChange(event);
  };

  return (
    <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id="demo-simple-select-label">{props.label}</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={val}
          label={props.label}
          defaultValue={props.defaultValue}
          onChange={handleChange}
        >
      {
          props.options.map((option, i) => {
              return <MenuItem value={option} key={i}>{option}</MenuItem>
          })
      }
        </Select>
      </FormControl>
    </Box>
  );
}
