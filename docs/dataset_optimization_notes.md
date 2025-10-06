# Dataset Optimization Notes for COLMAP

## Dataset Preparation for Lightning Strike Reconstruction

The Lightning Archive dataset has been specially prepared for 3D reconstruction of the lightning strike that occurred in New York City on June 26, 2024. This document provides guidance on optimizing the dataset for COLMAP reconstruction.

### Dataset Characteristics

- **Content**: 20-30 unique media items (videos/photos) capturing the same lightning strike event
- **Sources**: Multiple platforms (YouTube, Reddit, Twitter) providing diverse vantage points
- **Frame Selection**: Frames extracted at peak brightness moments to capture the lightning strike
- **Time Alignment**: All media is from the June 26, 2024 lightning event in NYC
- **Format**: High-resolution PNG images with consistent naming scheme

## Optimization Methods

### 1. Data Collection & Filtering

- **API Integration**: Multiple platform APIs (YouTube, Reddit, Twitter native, Twitter via RapidAPI) used with appropriate rate limiting and authentication
- **Search Expansion**: Wide range of search queries and subreddits to maximize relevant content
- **Temporal Filtering**: Client-side filtering to focus on content from June 26, 2024
- **Content Relevance**: Keyword filtering to ensure NYC lightning-related content

### 2. Media Processing

- **Intelligent Frame Extraction**: 
  - Peak brightness detection algorithm identifies lightning strikes
  - Brightness spikes detection to capture flash moments
  - Spatial brightness distribution analysis to differentiate lightning from other bright objects
  - Frame gap enforcement to avoid near-duplicate frames

- **Deduplication**: 
  - Image hashing (perceptual hashing via imagehash library) to identify duplicate or near-duplicate images
  - Content-based filtering to ensure unique vantage points

- **Metadata Enrichment**:
  - Timestamp extraction from video frames
  - Geolocation approximation where available
  - Resolution and quality metrics
  - Source tracking and attribution

### 3. Dataset Scoring & Selection

- **Scoring Algorithm**: Each frame is scored based on:
  - Resolution quality (higher resolution = better score)
  - Timestamp proximity to other frames (closer to synchronized moment = better score)
  - Vantage diversity (more diverse angles = better score)
  - Lightning visibility (clearer lightning strike = better score)

- **Selection Criteria**:
  - Top-scoring frames selected while maintaining minimum distance in time
  - Balancing between quality and diversity of vantage points
  - Ensuring sufficient feature overlap for COLMAP reconstruction

## COLMAP Optimization Tips

### Recommended COLMAP Workflow

1. **Initial Setup**:
   - Place the dataset images in the COLMAP workspace
   - Use the included metadata/colmap_info.json for initial camera parameters

2. **Feature Extraction**:
   - Use SIFT features with default parameters
   - Command: `colmap feature_extractor --database_path database.db --image_path images`
   - Consider increasing the number of features for lightning images (--SiftExtraction.max_num_features 8192)

3. **Feature Matching**:
   - Use exhaustive matching for this small dataset
   - Command: `colmap exhaustive_matcher --database_path database.db`
   - Adjust the match threshold to handle the brightness variations (--ExhaustiveMatcher.lowes_ratio 0.8)

4. **Sparse Reconstruction**:
   - Command: `colmap mapper --database_path database.db --image_path images --output_path sparse`
   - If reconstruction fails, try:
     - Lowering the min_num_matches threshold
     - Adding more images from different vantage points
     - Using guided matching with approximate camera positions

5. **Dense Reconstruction**:
   - Command: `colmap image_undistorter --image_path images --input_path sparse/0 --output_path dense`
   - Command: `colmap patch_match_stereo --workspace_path dense`
   - Command: `colmap stereo_fusion --workspace_path dense --output_path dense/fused.ply`

### Special Considerations for Lightning

- **High Dynamic Range**: Lightning creates extreme brightness variations
  - Consider using HDR tone mapping on frames before reconstruction
  - Try `--SiftExtraction.normalization true` to help with contrast differences

- **Transient Nature**: Lightning exists for a brief moment
  - Focus on frames with the clearest lightning visibility
  - Use frame synchronization to ensure all images capture the same moment

- **Feature Matching Challenges**: Lightning lacks traditional features
  - Use the surrounding buildings and skyline as anchor features
  - The NYC skyline provides excellent feature points for matching

## Reproducibility

- All processing steps are logged in `data/workflow_logs/`
- Configuration uses environment variables in `.env` file
- Original data sources are tracked in metadata
- Random seed values are fixed for deterministic processing

## Advanced COLMAP Options

For difficult reconstructions, try these advanced COLMAP parameters:

```
--Mapper.ba_global_images_ratio 1.32
--Mapper.ba_global_points_ratio 1.32
--Mapper.filter_max_reproj_error 4
--Mapper.init_min_num_inliers 15
--Mapper.multiple_models 1
--Mapper.extract_colors 1
```

## Output Visualization

After reconstruction, the lightning strike can be visualized using:
- MeshLab for point cloud and mesh viewing
- CloudCompare for analysis and measurements
- Blender for advanced rendering and animation

## Additional Resources

- [COLMAP Documentation](https://colmap.github.io/)
- [Multi-view Geometry in Computer Vision](https://www.robots.ox.ac.uk/~vgg/hzbook/)
- [Structure from Motion Revisited](https://demuc.de/papers/schoenberger2016sfm.pdf)

---

This dataset is part of the Lightning Archive project which aims to reconstruct the 3D structure of lightning strikes from crowd-sourced media. For questions, contact the project maintainers.
