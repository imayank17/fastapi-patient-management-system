import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function Patients() {
  const [patients, setPatients] = useState([]); // Now an array for easier rendering
  const [error, setError] = useState('');
  const [searchType, setSearchType] = useState('all');
  const [searchValue, setSearchValue] = useState('');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' or 'edit'
  const [formData, setFormData] = useState({
    id: '', name: '', city: '', age: '', gender: 'male', height: '', weight: ''
  });

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchPatients();
  }, [navigate]);

  const fetchPatients = async () => {
    try {
      const response = await api.get('/view');
      // Convert the backend dictionary { "P001": {...} } to an array for easy mapping
      const patientsArray = Object.entries(response.data).map(([id, data]) => ({
        id, ...data
      }));
      setPatients(patientsArray);
      setError('');
    } catch (err) {
      handleApiError(err, 'Failed to fetch patients.');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchType === 'all' || !searchValue.trim()) {
      fetchPatients();
      return;
    }

    try {
      let response;
      if (searchType === 'id') {
        response = await api.get(`/patients/search?patient_id=${searchValue}`);
        // Endpoint returns a single object
        setPatients([{ id: searchValue, ...response.data }]);
      } else if (searchType === 'name') {
        response = await api.get(`/patients/search/name?name=${searchValue}`);
        setPatients(response.data); // Returns an array
      } else if (searchType === 'city') {
        response = await api.get(`/patients/search/city?city=${searchValue}`);
        setPatients(response.data); // Returns an array
      }
      setError('');
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setPatients([]); // No results found
      } else {
        handleApiError(err, 'Search failed.');
      }
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete patient ${id}?`)) return;
    
    try {
      await api.delete(`/delete/${id}`);
      // Remove from local state immediately to avoid refetching
      setPatients(patients.filter(p => p.id !== id));
    } catch (err) {
      handleApiError(err, 'Failed to delete patient.');
    }
  };

  const openAddModal = () => {
    setModalMode('add');
    setFormData({ id: '', name: '', city: '', age: '', gender: 'male', height: '', weight: '' });
    setShowModal(true);
  };

  const openEditModal = (patient) => {
    setModalMode('edit');
    setFormData({ ...patient });
    setShowModal(true);
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    try {
      if (modalMode === 'add') {
        await api.post('/create', formData);
      } else {
        // Exclude ID from payload as per schema requirement
        const { id, bmi, verdict, ...updateData } = formData;
        await api.put(`/edit/${id}`, updateData);
      }
      setShowModal(false);
      // Re-fetch patients to get updated BMI/verdict from DB
      fetchPatients(); 
    } catch (err) {
      handleApiError(err, `Failed to ${modalMode} patient.`);
    }
  };

  const handleApiError = (err, defaultMsg) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('token');
      navigate('/login');
    } else {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0].msg : (detail || defaultMsg));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="container" style={{ maxWidth: '900px' }}>
      <div className="header">
        <h2>Patient Dashboard</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>
      
      {/* Search and Action Bar */}
      <div className="action-bar">
        <form onSubmit={handleSearch} className="search-form">
          <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
            <option value="all">View All</option>
            <option value="id">Search by ID</option>
            <option value="name">Search by Name</option>
            <option value="city">Search by City</option>
          </select>
          {searchType !== 'all' && (
            <input 
              type="text" 
              placeholder={`Enter ${searchType}...`} 
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              required
            />
          )}
          <button type="submit" className="search-btn">Search</button>
        </form>
        <button onClick={openAddModal} className="add-btn">+ Add Patient</button>
      </div>

      {error && <div className="error">{error}</div>}
      
      {/* Patient List */}
      <div className="patients-list">
        {patients.length === 0 ? (
          <div className="no-data">No patients found.</div>
        ) : (
          patients.map((patient) => (
            <div key={patient.id} className="patient-card">
              <div className="card-header">
                <h3>{patient.name} <span className="patient-id">({patient.id})</span></h3>
                <div className="card-actions">
                  <button onClick={() => openEditModal(patient)} className="edit-btn">Edit</button>
                  <button onClick={() => handleDelete(patient.id)} className="delete-btn">Delete</button>
                </div>
              </div>
              <div className="patient-details">
                <p><strong>Age:</strong> {patient.age}</p>
                <p><strong>Gender:</strong> {patient.gender}</p>
                <p><strong>City:</strong> {patient.city}</p>
                <p><strong>Height:</strong> {patient.height}m</p>
                <p><strong>Weight:</strong> {patient.weight}kg</p>
                <p><strong>BMI:</strong> <span className="tag bmi-tag">{patient.bmi?.toFixed(2)}</span></p>
                <p><strong>Verdict:</strong> <span className={`tag verdict-${patient.verdict?.toLowerCase()}`}>{patient.verdict}</span></p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal for Add/Edit */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>{modalMode === 'add' ? 'Add New Patient' : `Edit Patient (${formData.id})`}</h3>
            <form onSubmit={handleModalSubmit}>
              {modalMode === 'add' && (
                <div className="form-group">
                  <label>Patient ID</label>
                  <input type="text" name="id" value={formData.id} onChange={handleFormChange} required placeholder="e.g. P001" />
                </div>
              )}
              <div className="form-group">
                <label>Name</label>
                <input type="text" name="name" value={formData.name} onChange={handleFormChange} required />
              </div>
              <div className="form-group">
                <label>City</label>
                <input type="text" name="city" value={formData.city} onChange={handleFormChange} required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Age</label>
                  <input type="number" name="age" value={formData.age} onChange={handleFormChange} required min="0" />
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select name="gender" value={formData.gender} onChange={handleFormChange}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Height (m)</label>
                  <input type="number" step="0.01" name="height" value={formData.height} onChange={handleFormChange} required min="0.1" />
                </div>
                <div className="form-group">
                  <label>Weight (kg)</label>
                  <input type="number" step="0.1" name="weight" value={formData.weight} onChange={handleFormChange} required min="1" />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="cancel-btn">Cancel</button>
                <button type="submit" className="save-btn">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Patients;
