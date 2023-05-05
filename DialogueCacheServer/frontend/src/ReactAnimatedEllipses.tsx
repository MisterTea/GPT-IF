import 'animated-ellipsis';
import PropTypes from 'prop-types';
import React from 'react';

function ReactAnimatedEllipsis(props: any) {
  const { style, className, marginLeft, spacing, fontSize } = props;

  const wrapperRef = React.createRef<any>();

  React.useEffect(() => {
    const { current } = wrapperRef;
    current.animateEllipsis();
    return () => current.stopAnimatingEllipsis();
  }, [wrapperRef]);

  return (
    <span
      ref={wrapperRef}
      className={className}
      style={fontSize ? { ...style, fontSize } : style}
      data-margin-left={marginLeft}
      data-spacing={spacing}
    />
  );
}

ReactAnimatedEllipsis.propTypes = {
  style: PropTypes.object,
  className: PropTypes.string,
  fontSize: PropTypes.string,
  marginLeft: PropTypes.string,
  spacing: PropTypes.string
};

ReactAnimatedEllipsis.defaultProps = {
  style: {},
  className: '',
  fontSize: '2rem',
  marginLeft: '0.1rem',
  spacing: '0.1rem'
};

export default ReactAnimatedEllipsis;
